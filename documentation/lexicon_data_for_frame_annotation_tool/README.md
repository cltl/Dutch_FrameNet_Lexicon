# FrameNet input to annotation tool

This directory contains three files:
* **frame_to_info.json**
* **lu_to_frames.json**
* **lu_and_pos_to_frames**

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

## **lu_to_frames.json**

In this current version, a **lemma** is mapped to its candidate frame IDs according to FrameNet 1.7 as part of [PreMOn](https://premon.fbk.eu/), e.g.,

```json
"sail": [
    "http://premon.fbk.eu/resource/fn17-self_motion",
    "http://premon.fbk.eu/resource/fn17-ride_vehicle",
    "http://premon.fbk.eu/resource/fn17-operate_vehicle"
],
"sailor": [
    "http://premon.fbk.eu/resource/fn17-member_of_military"
],
```

* **lu_and_pos_to_frames**

## Considerations
* do we use the part of speech in the look-up and if so NAF or Universal Dependencies?
* what kind of identifiers do we use for FrameNet lexical units, roles, and frames? Framester or other one.
* how do we vizualize the information to the annotators? Which information do we show?
* how do deal with multiword expressions? How do we represent them?