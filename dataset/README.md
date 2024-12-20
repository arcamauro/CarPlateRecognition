# Cognitechna License Plate dataset

Small dataset of license plate images captured in Brno.

- Mostly Czech license plates
- Each image contain one or more objects
- Each object is defined by location of four corners, text and type

## Attributes

- `text` - Automatically read by OCR so it may not be always accurate. You can try to filter out those that look promising - correct number of letters, regexp matches CZ or SK patterns. But there is not enough data train accurate OCR. If text is empty string, it was not processed by OCR.
- `type` - Type of license plate. E.g. `SINGLE` for single line plates, or `DOUBLE` for two line plates.
- `points` - Coordinates of license plate corners [[x,y],[x,y],[x,y],[x,y]] with order: Top-left, Top-right, Bottom-right, Bottom-left.

The annotations are stored in JSON object, mapping filename to a list of dictionary objects.

```json
{
"image.jpg": [
    {
        "text": "1AB2345",
        "type": "SINGLE",
        "points": [[1,2],[3,4],[5,6],[7,8]]
    },
    {...}
],
"another_image": [ ... ]
}
```