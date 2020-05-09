# FrameNet input to annotation tool

This directory contains three files:
* **frame_to_info.json**
* **part_of_speech_ud_info.json**
* **ud_pos_to_fn_pos.json**

## **frame_to_info.json**

A frame [PreMOn](https://premon.fbk.eu/) URI is mapped to its definition, and Frame Element information, e.g.,
```json
 "http://premon.fbk.eu/resource/fn17-access_scenario": {
        "definition": "A Theme is or is not capable of entering or accessing a Useful_location because of/despite a Barrier.",
        "frame_elements": [
            {
                "definition": "The Theme whose motion is blocked or free.  ",
                "fe_label": "Theme",
                "fe_type": "Core",
                "rdf_uri": "http://premon.fbk.eu/resource/fn17-access_scenario@theme"
            },
            {
                "definition": "The place or thing that the Theme is headed towards, despite a potential or actual Barrier.",
                "fe_label": "Useful_location",
                "fe_type": "Core",
                "rdf_uri": "http://premon.fbk.eu/resource/fn17-access_scenario@useful_location"
            },
            {
                "definition": "An entity that (at least potentially) prevents the Theme from getting to the Useful_location. ",
                "fe_label": "Barrier",
                "fe_type": "Core",
                "rdf_uri": "http://premon.fbk.eu/resource/fn17-access_scenario@barrier"
            }
        ],
        "frame_label": "Access_scenario",
        "framenet_url": "https://framenet2.icsi.berkeley.edu/fnReports/data/frame/Access_scenario.xml"
    },
```

## **part_of_speech_ud_info.json**
Information about each UD part of speech tag.

## **ud_pos_to_fn_pos.json**
Mapping from UD part of speech tags to FrameNet part of speech tags.
