// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQTESTTOUCH_H
#define PYSIDEQTESTTOUCH_H

#include <QtTest/qttestglobal.h>
#include <QtTest/qtestassert.h>
#include <QtTest/qtestsystem.h>
#include <QtTest/qtestspontaneevent.h>
#include <QtTest/qtesttouch.h>

#include <QtCore/qmap.h>
#include <QtGui/qevent.h>
#include <QtGui/qwindow.h>
#ifdef QT_WIDGETS_LIB
#include <QtWidgets/qwidget.h>
#endif

QT_BEGIN_NAMESPACE

namespace QTest
{

    class PySideQTouchEventSequence
    {
    public:
        ~PySideQTouchEventSequence()
        {
            if (commitWhenDestroyed)
                commit();
        }
        PySideQTouchEventSequence *press(int touchId, const QPoint &pt, QWindow *window = nullptr)
        {
            auto it = m_points.find(touchId);
            if (it == m_points.end()) {
                QEventPoint point(touchId, QEventPoint::Pressed, pt, mapToScreen(window, pt));
                m_points.insert(touchId, point);
            }
            return this;
        }
        PySideQTouchEventSequence *move(int touchId, const QPoint &pt, QWindow *window = nullptr)
        {
            QEventPoint point(touchId, QEventPoint::Updated, pt, mapToScreen(window, pt));
            m_points[touchId] = point;
            return this;
        }
        PySideQTouchEventSequence *release(int touchId, const QPoint &pt, QWindow *window = nullptr)
        {
            auto it = m_points.find(touchId);
            if (it == m_points.end()) {
                QEventPoint point(touchId, QEventPoint::Released, pt, mapToScreen(window, pt));
                m_points.insert(touchId, point);
            }
            return this;
        }
        PySideQTouchEventSequence *stationary(int touchId)
        {
            auto it = m_points.find(touchId);
            if (it == m_points.end()) {
                auto previous_it = m_previousPoints.find(touchId);
                const QEventPoint point = previous_it != m_previousPoints.end()
                    ? previous_it.value()
                    : QEventPoint(touchId, QEventPoint::Stationary, QPointF(), QPointF());
                m_points.insert(touchId, point);
            }
            return this;
        }

#ifdef QT_WIDGETS_LIB
        PySideQTouchEventSequence *press(int touchId, const QPoint &pt, QWidget *widget = nullptr)
        {
            auto it = m_points.find(touchId);
            if (it == m_points.end()) {
                QEventPoint point(touchId, QEventPoint::Pressed, pt, mapToScreen(widget, pt));
                m_points.insert(touchId, point);
            }
            return this;
        }

        PySideQTouchEventSequence *move(int touchId, const QPoint &pt, QWidget *widget = nullptr)
        {
            QEventPoint point(touchId, QEventPoint::Updated, pt, mapToScreen(widget, pt));
            m_points[touchId] = point;
            return this;
        }

        PySideQTouchEventSequence *release(int touchId, const QPoint &pt, QWidget *widget = nullptr)
        {
            auto it = m_points.find(touchId);
            if (it == m_points.end()) {
                QEventPoint point(touchId, QEventPoint::Released, pt, mapToScreen(widget, pt));
                m_points.insert(touchId, point);
            }
            return this;
        }
#endif

        void commit(bool processEvents = true)
        {
            if (!m_points.isEmpty()) {
                if (targetWindow) {
                    qt_handleTouchEvent(targetWindow, device, m_points.values());
                }
#ifdef QT_WIDGETS_LIB
                else if (targetWidget) {
                    qt_handleTouchEvent(targetWidget->windowHandle(), device, m_points.values());
                }
#endif
            }
            if (processEvents)
                QCoreApplication::processEvents();
            m_previousPoints = m_points;
            m_points.clear();
        }

private:
#ifdef QT_WIDGETS_LIB
        PySideQTouchEventSequence(QWidget *widget, QPointingDevice *aDevice, bool autoCommit)
            : targetWidget(widget), device(aDevice), commitWhenDestroyed(autoCommit)
        {
        }
#endif
        PySideQTouchEventSequence(QWindow *window, QPointingDevice *aDevice, bool autoCommit)
            : targetWindow(window), device(aDevice), commitWhenDestroyed(autoCommit)
        {
        }

#ifdef QT_WIDGETS_LIB
        QPointF mapToScreen(const QWidget *widget, const QPointF &pt)
        {
            if (widget)
                return widget->mapToGlobal(pt);
            return targetWidget ? targetWidget->mapToGlobal(pt) : pt;
        }
#endif
        QPointF mapToScreen(const QWindow *window, const QPointF &pt)
        {
            if(window)
                return window->mapToGlobal(pt);
            return targetWindow ? targetWindow->mapToGlobal(pt) : pt;
        }

        QMap<int, QEventPoint> m_previousPoints;
        QMap<int, QEventPoint> m_points;
#ifdef QT_WIDGETS_LIB
        QWidget *targetWidget = nullptr;
#endif
        QWindow *targetWindow = nullptr;
        QPointingDevice *device = nullptr;
        bool commitWhenDestroyed = false;
#ifdef QT_WIDGETS_LIB
        friend PySideQTouchEventSequence *generateTouchEvent(QWidget *, QPointingDevice *, bool);
#endif
        friend PySideQTouchEventSequence *generateTouchEvent(QWindow *, QPointingDevice *, bool);
    };

#ifdef QT_WIDGETS_LIB
    inline
    PySideQTouchEventSequence *generateTouchEvent(QWidget *widget,
                                                  QPointingDevice *device,
                                                  bool autoCommit = true)
    {
        return new PySideQTouchEventSequence(widget, device, autoCommit);
    }
#endif
    inline
    PySideQTouchEventSequence *generateTouchEvent(QWindow *window,
                                                  QPointingDevice *device,
                                                  bool autoCommit = true)
    {
        return new PySideQTouchEventSequence(window, device, autoCommit);
    }

}

QT_END_NAMESPACE

#endif // PYSIDEQTESTTOUCH_H
