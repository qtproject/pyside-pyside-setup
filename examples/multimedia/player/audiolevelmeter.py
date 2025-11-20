# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from math import log10, sqrt
from PySide6.QtMultimedia import QAudioBuffer
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy, QToolButton,
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QBrush, QPainter, QPalette
from PySide6.QtCore import QObject, QRectF, QThread, QTimer, qFuzzyCompare, Qt, Signal, Slot


# Constants used by AudioLevelMeter and MeterChannel
WIDGET_WIDTH = 34
MAX_CHANNELS = 8
PEAK_COLOR = "#1F9B5D"
RMS_COLOR = "#28C878"
RMS_WINDOW = 400  # ms
PEAK_LABEL_HOLD_TIME = 2000  # ms
DECAY_EASE_IN_TIME = 160  # ms
UPDATE_INTERVAL = 16  # ms, Assuming 60 Hz refresh rate.
DB_DECAY_PER_SECOND = 20.0
DB_DECAY_PER_UPDATE = DB_DECAY_PER_SECOND / (1000 / UPDATE_INTERVAL)
DB_MAX = 0.0
DB_MIN = -60.0


def amplitudeToDb(f):
    """Converts a float sample value to dB and clamps it between DB_MIN and DB_MAX."""
    if f <= 0:
        return DB_MIN
    v = 20.0 * log10(f)
    if v < DB_MIN:
        return DB_MIN
    if v > DB_MAX:
        return DB_MAX
    return v


# A struct used by BufferAnalyzer to emit its results back to AudioLevelMeter
class BufferValues:
    """A struct used by BufferAnalyzer to emit its results back to AudioLevelMeter."""
    def __init__(self, nChannels):
        self.peaks = [0.0] * nChannels
        self.squares = [0.0] * nChannels


class BufferAnalyzer(QObject):
    """A worker class analyzing incoming buffers on a separate worker thread."""
    valuesReady = Signal(BufferValues)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_stopRequested = False

    def requestStop(self):
        self.m_stopRequested = True

    @Slot(QAudioBuffer, int)
    def analyzeBuffer(self, buffer, maxChannelsToAnalyze):
        """Analyzes an audio buffer and emits its peak and sumOfSquares values.
           Skips remaining frames if self.m_stopRequested is set to true."""

        if QThread.currentThread().isInterruptionRequested():
            return  # Interrupted by ~AudioLevelMeter, skipping remaining buffers in signal queue

        self.m_stopRequested = False

        channelCount = buffer.format().channelCount()
        channelsToAnalyze = min(channelCount, maxChannelsToAnalyze)

        values = BufferValues(channelsToAnalyze)

        bufferData = buffer.constData()
        bufferSize = len(bufferData)
        bytesPerSample = buffer.format().bytesPerSample()

        for i in range(0, bufferSize, bytesPerSample * channelCount):
            if self.m_stopRequested:
                framesSkipped = (bufferSize - i) / channelCount
                print("BufferAnalyzer::analyzeBuffer skipped", framesSkipped, "out of",
                      buffer.frameCount(), "frames")
                # Emit incomplete values also when stop is requested to get some audio level readout
                # even if frames are being skipped for every buffer. Displayed levels will be
                # inaccurate.
                break

            for channelIndex in range(0, channelsToAnalyze):
                offset = i + bytesPerSample * channelIndex
                sample = buffer.format().normalizedSampleValue(bufferData[offset:])
                values.peaks[channelIndex] = max(values.peaks[channelIndex], abs(sample))
                values.squares[channelIndex] += sample * sample

        self.valuesReady.emit(values)


class MeterChannel(QWidget):
    """A custom QWidget representing an audio channel in the audio level meter. It serves
       both as a model for the channels's peak and RMS values and as a view using the overridden
       paintEvent()."""
    def __init__(self, parent):
        super().__init__(parent)
        self.m_peakDecayRate = 0.0
        self.m_rmsDecayRate = 0.0
        self.m_peak = DB_MIN
        self.m_rms = DB_MIN
        self.m_sumOfSquares = 0.0
        self.m_sumOfSquaresQueue = []
        self.m_peakBrush = QBrush(PEAK_COLOR)
        self.m_rmsBrush = QBrush(RMS_COLOR)

    def normalize(self, dB):
        """# Normalizes a dB value for visualization."""
        return (dB - DB_MIN) / (DB_MAX - DB_MIN)

    def clearRmsData(self):
        """Clears the data used to calculate RMS values."""
        self.m_sumOfSquares = 0.0
        self.m_sumOfSquaresQueue = []

    def decayPeak(self):
        """Decays self.m_peak value by DB_DECAY_PER_UPDATE with ease-in animation based
           on DECAY_EASE_IN_TIME."""
        peak = self.m_peak
        if qFuzzyCompare(peak, DB_MIN):
            return

        cubicEaseInFactor = self.m_peakDecayRate * self.m_peakDecayRate * self.m_peakDecayRate
        self.m_peak = max(DB_MIN, peak - DB_DECAY_PER_UPDATE * cubicEaseInFactor)

        if self.m_peakDecayRate < 1:
            self.m_peakDecayRate += float(UPDATE_INTERVAL) / float(DECAY_EASE_IN_TIME)
            if self.m_peakDecayRate > 1.0:
                self.m_peakDecayRate = 1.0

    def decayRms(self):
        """Decays self.m_rms value by DB_DECAY_PER_UPDATE with ease-in animation based on
           DECAY_EASE_IN_TIME."""
        rms = self.m_rms
        if qFuzzyCompare(rms, DB_MIN):
            return

        cubicEaseInFactor = self.m_rmsDecayRate * self.m_rmsDecayRate * self.m_rmsDecayRate
        self.m_rms = max(DB_MIN, rms - DB_DECAY_PER_UPDATE * cubicEaseInFactor)

        if self.m_rmsDecayRate < 1:
            self.m_rmsDecayRate += float(UPDATE_INTERVAL) / float(DECAY_EASE_IN_TIME)
            if self.m_rmsDecayRate > 1.0:
                self.m_rmsDecayRate = 1.0

    def updatePeak(self, sampleValue):
        """Updates self.m_peak and resets self.m_peakDecayRate if sampleValue > self.m_peak."""
        dB = amplitudeToDb(sampleValue)
        if dB > self.m_peak:
            self.m_peakDecayRate = 0
            self.m_peak = dB

    def updateRms(self, sumOfSquaresForOneBuffer, duration, frameCount):
        """Calculates current RMS. Resets self.m_rmsDecayRate and updates self.m_rms
           if current RMS > self.m_rms."""

        # Add the new sumOfSquares to the queue and update the total
        self.m_sumOfSquaresQueue.append(sumOfSquaresForOneBuffer)
        self.m_sumOfSquares += sumOfSquaresForOneBuffer

        # Remove the oldest sumOfSquares to stay within the RMS window
        if len(self.m_sumOfSquaresQueue) * duration > RMS_WINDOW:
            self.m_sumOfSquares -= self.m_sumOfSquaresQueue[0]
            del self.m_sumOfSquaresQueue[0]

        # Fix negative values caused by floating point precision errors
        if self.m_sumOfSquares < 0:
            self.m_sumOfSquares = 0

        # Calculate the new RMS value
        if self.m_sumOfSquares > 0 and self.m_sumOfSquaresQueue:
            newRms = sqrt(self.m_sumOfSquares / (frameCount * len(self.m_sumOfSquaresQueue)))
            dB = amplitudeToDb(newRms)
            if dB > self.m_rms:
                self.m_rmsDecayRate = 0
                self.m_rms = dB

    def paintEvent(self, event):
        """Paints the level bar of the meter channel based on the decayed peak and rms values."""
        if qFuzzyCompare(self.m_peak, DB_MIN) and qFuzzyCompare(self.m_rms, DB_MIN):
            return  # Nothing to paint

        peakLevel = self.normalize(self.m_peak)
        rmsLevel = self.normalize(self.m_rms)

        with QPainter(self) as painter:
            rect = QRectF(0, self.height(), self.width(), -peakLevel * self.height())
            painter.fillRect(rect, self.m_peakBrush)  # Paint the peak level
            rect.setHeight(-rmsLevel * self.height())
            painter.fillRect(rect, self.m_rmsBrush)  # Paint the RMS level


class AudioLevelMeter(QWidget):
    """The audio level meter´s parent widget class. It acts as a controller
       for the MeterChannel widgets and the BufferAnalyzer worker."""

    newBuffer = Signal(QAudioBuffer, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_isOn = True
        self.m_isActive = False
        self.m_channels = []
        self.m_channelCount = 0
        self.m_bufferDurationMs = 0
        self.m_frameCount = 0
        self.m_highestPeak = 0.0
        self.m_updateTimer = QTimer()
        self.m_deactivationTimer = QTimer()
        self.m_peakLabelHoldTimer = QTimer()
        self.m_peakLabel = None
        self.m_onOffButton = None
        self.m_bufferAnalyzer = None
        self.m_analyzerThread = QThread()

        # Layout and background color
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(WIDGET_WIDTH)
        currentPalette = self.palette()
        currentPalette.setColor(QPalette.ColorRole.Window,
                                currentPalette.color(QPalette.ColorRole.Base))
        self.setPalette(currentPalette)
        self.setAutoFillBackground(True)
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Meter channels
        meterChannelLayout = QHBoxLayout()
        meterChannelLayout.setContentsMargins(2, 2, 2, 2)
        meterChannelLayout.setSpacing(2)
        for i in range(0, MAX_CHANNELS):
            channel = MeterChannel(self)
            meterChannelLayout.addWidget(channel)
            self.m_channels.append(channel)
        mainLayout.addLayout(meterChannelLayout)

        # Peak label
        self.m_peakLabel = QLabel("-", self)
        self.m_peakLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QApplication.font()
        font.setPointSize(10)
        self.m_peakLabel.setFont(font)
        mainLayout.addWidget(self.m_peakLabel)
        mainLayout.setStretch(0, 1)

        # On/off button
        self.m_onOffButton = QToolButton(self)
        mainLayout.addWidget(self.m_onOffButton)
        self.m_onOffButton.setMaximumWidth(WIDGET_WIDTH)
        self.m_onOffButton.setText("On")
        self.m_onOffButton.setCheckable(True)
        self.m_onOffButton.setChecked(True)
        self.m_onOffButton.clicked.connect(self.toggleOnOff)

        # Timer triggering update of the audio level bars
        self.m_updateTimer.timeout.connect(self.updateBars)

        # Timer postponing deactivation of update timer to allow meters to fade to 0
        self.m_deactivationTimer.timeout.connect(self.m_updateTimer.stop)
        self.m_deactivationTimer.setSingleShot(True)

        # Timer resetting the peak label
        self.m_peakLabelHoldTimer.timeout.connect(self.resetPeakLabel)
        self.m_peakLabelHoldTimer.setSingleShot(True)

        # Buffer analyzer and worker thread that analyzes incoming buffers
        self.m_bufferAnalyzer = BufferAnalyzer()
        self.m_bufferAnalyzer.moveToThread(self.m_analyzerThread)
        self.m_analyzerThread.finished.connect(self.m_bufferAnalyzer.deleteLater)
        self.newBuffer.connect(self.m_bufferAnalyzer.analyzeBuffer)
        self.m_bufferAnalyzer.valuesReady.connect(self.updateValues)
        self.m_analyzerThread.start()

    def closeRequest(self):
        self.m_analyzerThread.requestInterruption()
        self.m_bufferAnalyzer.requestStop()
        self.m_analyzerThread.quit()
        self.m_analyzerThread.wait()

    @Slot(QAudioBuffer)
    def onAudioBufferReceived(self, buffer):
        """Receives a buffer from QAudioBufferOutput and triggers BufferAnalyzer to analyze it."""
        if not self.m_isOn or not buffer.isValid() or not buffer.format().isValid():
            return

        if not self.m_isActive:
            self.activate()

        # Update internal values to match the current audio stream
        self.updateChannelCount(buffer.format().channelCount())
        self.m_frameCount = buffer.frameCount()
        self.m_bufferDurationMs = buffer.duration() / 1000

        # Stop any ongoing analysis, skipping remaining frames
        self.m_bufferAnalyzer.requestStop()

        self.newBuffer.emit(buffer, self.m_channelCount)

    @Slot(BufferValues)
    def updateValues(self, values):
        """Updates peak/RMS values and peak label."""
        if not self.m_isActive:
            return  # Discard incoming values from BufferAnalyzer

        bufferPeak = 0.0
        for i in range(0, len(values.peaks)):
            bufferPeak = max(bufferPeak, values.peaks[i])
            self.m_channels[i].updatePeak(values.peaks[i])
            self.m_channels[i].updateRms(values.squares[i], self.m_bufferDurationMs,
                                         self.m_frameCount)
        self.updatePeakLabel(bufferPeak)

    def updatePeakLabel(self, peak):
        """Updates peak label and restarts self.m_peakLabelHoldTimer
           if peak >= self.m_highestPeak."""
        if peak < self.m_highestPeak:
            return

        self.m_peakLabelHoldTimer.start(PEAK_LABEL_HOLD_TIME)

        if qFuzzyCompare(peak, self.m_highestPeak):
            return

        self.m_highestPeak = peak
        dB = amplitudeToDb(self.m_highestPeak)
        self.m_peakLabel.setText(f"{int(dB)}")

    @Slot()
    def resetPeakLabel(self):
        """Resets peak label. Called when self.m_labelHoldTimer timeouts."""
        self.m_highestPeak = 0.0
        self.m_peakLabel.setText(f"{DB_MIN}" if self.m_isOn else "")

    def clearAllRmsData(self):
        """Clears internal data used to calculate RMS values."""
        for channel in self.m_channels.copy():
            channel.clearRmsData()

    @Slot()
    def activate(self):
        """Starts the update timer that updates the meter bar."""
        self.m_isActive = True
        self.m_deactivationTimer.stop()
        self.m_updateTimer.start(UPDATE_INTERVAL)

    @Slot()
    def deactivate(self):
        """Start the deactiviation timer that eventually stops the update timer."""
        self.m_isActive = False
        self.clearAllRmsData()
        # Calculate the time it takes to decay fram max to min dB
        interval = (DB_MAX - DB_MIN) / (DB_DECAY_PER_SECOND / 1000) + DECAY_EASE_IN_TIME
        self.m_deactivationTimer.start(interval)

    @Slot()
    def updateBars(self):
        """Decays internal peak and RMS values and triggers repainting of meter bars."""
        for i in range(0, self.m_channelCount):
            channel = self.m_channels[i]
            channel.decayPeak()
            channel.decayRms()
            channel.update()  # Trigger paint event

    @Slot()
    def toggleOnOff(self):
        """Toggles between on (activated) and off (deactivated) state."""
        self.m_isOn = not self.m_isOn
        if not self.m_isOn:
            self.deactivate()
        else:
            self.activate()
        self.m_onOffButton.setText("On" if self.m_isOn else "Off")

    def updateChannelCount(self, channelCount):
        """Updates the number of visible MeterChannel widgets."""
        if (channelCount == self.m_channelCount
                or (channelCount > MAX_CHANNELS and MAX_CHANNELS == self.m_channelCount)):
            return

        self.m_channelCount = min(channelCount, MAX_CHANNELS)
        for i in range(0, MAX_CHANNELS):
            self.m_channels[i].setVisible(i < self.m_channelCount)
