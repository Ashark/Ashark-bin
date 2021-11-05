#!/bin/bash

# Author: Andrew Shark
# Homepage: https://github.com/Ashark/Ashark-bin
# License: GPLv3

# This script is made to relaunch app after close, mimicking close to tray.
# See https://github.com/user-none/KDocker/issues/97 for the kdocker feature request.

# TODO Make a kwin script instead of this?
# Currently an infinite loop process (this script) is launched, which you should manually stop at will.
# The kwin script could just launch a command to start app at app window closed.

# Edit your app of interest as follows (assuming it is gnome sound recorder):
# cp /usr/share/applications/org.gnome.SoundRecorder.desktop ~/.local/share/applications/org.gnome.SoundRecorder.desktop
# Open ~/.local/share/applications/org.gnome.SoundRecorder.desktop in kate and edit
# Exec=gnome-sound-recorder
# to
# Exec=QT_QPA_PLATFORM=xcb konsole -e /home/andrew/bin/kdocker-fake-close-to-tray.sh gnome-sound-recorder
# Of course, edit the path to your home dir.
# Place this script to your home bin dir, as in my example: /home/andrew/bin/kdocker-fake-close-to-tray.sh

app_name="$1"

# We want to allow only one instance of fake-ctt per app
LOCKDIR=/tmp/fake-ctt_$app_name
#Remove the lock directory
function cleanup {
    if rmdir $LOCKDIR; then
        echo "Finished"
    else
        echo "Failed to remove lock directory '$LOCKDIR'"
        sleep 10
        exit 1
    fi
}

if mkdir $LOCKDIR; then
    #Ensure that if we "grabbed a lock", we release it
    #Works for SIGTERM and SIGINT(Ctrl-C)
    trap "cleanup" EXIT

    echo "Acquired lock, running"

    keep_window_showing="-m"

    while true; do
        ps --no-headers -C "kdocker $app_name" -o args,state
        exit_code=$?
        if [[ $exit_code != 0 ]]; then
            if [[ "$keep_window_showing" == "" ]]; then
                kdialog --title "kdocker fake close to tray $$" --passivepopup "The app was closed, relaunching minimized to tray" 5
                echo "The app was closed, relaunching minimized to tray"
            else
                echo "Launching first time, keeping window shown"
            fi
            # TODO Here need to create and apply a window rule for the app window. The rule is "minimized - apply initialy". So when app is relaunch, it is not shown for a second before traying.
            QT_QPA_PLATFORM=xcb GDK_BACKEND=x11 kdocker $keep_window_showing "$app_name"
            keep_window_showing=""
        else
            echo "something went wrong"
            echo "probably undocked instance of app exists, killing it."
            killall "$app_name"
            sleep 1
#             exit 1
        fi
    done

else
    echo "Could not create lock directory '$LOCKDIR'"
    sleep 3
    exit 1
fi
