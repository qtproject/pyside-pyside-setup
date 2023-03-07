// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtPositioning

LocaleForm {
    property string locale
    signal selectLanguage(string language)
    signal closeForm()

    goButton.onClicked: {

       if (!languageGroup.checkedButton) return

       if (otherRadioButton.checked) {
           selectLanguage(language.text)
       } else {
           selectLanguage(languageGroup.checkedButton.text)
       }
    }

    clearButton.onClicked: {
        language.text = ""
    }

    cancelButton.onClicked: {
        closeForm()
    }

    Component.onCompleted: {
        switch (locale) {
            case "en":
                enRadioButton.checked = true;
                break
            case "fr":
                frRadioButton.checked = true;
                break
            default:
                otherRadioButton.checked = true;
                language.text = locale
                break
        }
    }
}
