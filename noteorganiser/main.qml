import QtQuick 2.2
import Material 0.1
import Material.ListItems 0.1 as ListItem

ApplicationWindow {
    id: noteorganiser

    title: "Note Organiser"

    // Necessary when loading the window from C++
    visible: true

    theme {
        primaryColor: Palette.colors["blue"]["500"]
        primaryDarkColor: Palette.colors["blue"]["700"]
        accentColor: Palette.colors["red"]["A200"]
        tabHighlightColor: "white"
    }

    initialPage: Page {
        id: page

        title: "Current Note"

        actions: [
            Action {
                iconName: "content/add"
                name: "New Post"
            },

            Action {
                iconName: "content/archive"
                name: "Export to html"
            },

            Action {
                iconName: "action/build"
                name: "Settings"
                hoverAnimation: true
            },

            Action {
                iconName: "image/color_lens"
                name: "Colors"
                onTriggered: colorPicker.show()
            }

        ]

        Sidebar {
            id: navSidebar

            Label {
              font.family: "Roboto"
              font.weight: Font.DemiBold
              text: "Files"
              font.pixelSize: Units.dp(20)

              anchors {
                left: parent.left
                margins: Units.dp(34)
              }
            }
        }

        Flickable {
            id: flickable
            anchors {
                left: navSidebar.right
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            clip: true
            contentHeight: Math.max(example.implicitHeight + 40, height)

            Loader {
                id: example
                anchors.fill: parent
                asynchronous: true
                visible: status == Loader.Ready
                // selectedComponent will always be valid, as it defaults to the first component
                source: {
                    if (navDrawer.enabled) {
                        return Qt.resolvedUrl("%1Demo.qml").arg(demo.selectedComponent.replace(" ", ""))
                    } else {
                        return Qt.resolvedUrl("%1Demo.qml").arg(selectedComponent.replace(" ", ""))
                    }
                }
            }

            ProgressCircle {
                anchors.centerIn: parent
                visible: example.status == Loader.Loading
            }
        }
        Scrollbar {
            flickableItem: flickable
        }
        Sidebar {
            id: tagSidebar

            anchors {
                left: fickable.right
                right: parent.right
                top: parent.top
                bottom: parent.bottom
            }
            expanded: !navDrawer.enabled

        }
    }

    Dialog {
        id: colorPicker
        title: "Pick color"

        positiveButtonText: "Done"

        MenuField {
            id: selection
            model: ["Primary color", "Accent color", "Background color"]
            width: Units.dp(160)
        }

        Grid {
            columns: 7
            spacing: Units.dp(8)

            Repeater {
                model: [
                    "red", "pink", "purple", "deepPurple", "indigo",
                    "blue", "lightBlue", "cyan", "teal", "green",
                    "lightGreen", "lime", "yellow", "amber", "orange",
                    "deepOrange", "grey", "blueGrey", "brown", "black",
                    "white"
                ]

                Rectangle {
                    width: Units.dp(30)
                    height: Units.dp(30)
                    radius: Units.dp(2)
                    color: Palette.colors[modelData]["500"]
                    border.width: modelData === "white" ? Units.dp(2) : 0
                    border.color: Theme.alpha("#000", 0.26)

                    Ink {
                        anchors.fill: parent

                        onPressed: {
                            switch(selection.selectedIndex) {
                                case 0:
                                    theme.primaryColor = parent.color
                                    break;
                                case 1:
                                    theme.accentColor = parent.color
                                    break;
                                case 2:
                                    theme.backgroundColor = parent.color
                                    break;
                            }
                        }
                    }
                }
            }
        }

        onRejected: {
            // TODO set default colors again but we currently don't know what that is
        }
    }

}

