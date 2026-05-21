// @snippet qhttpheaders-rangevalues
Returns the values of the *Range* HTTP header field, parsed as a list of
tuples.

Each range represents a byte range. According to RFC 9110:

* If the start is specified but the end is not (e.g., ``"bytes=500-"``),
  the tuple will have ``start=500`` and ``end=None``.
* If the end is specified but the start is not (e.g., ``"bytes=-500"``),
  the tuple will have ``start=None`` and ``end=500``,
  representing the last 500 bytes.
* If both are specified (e.g., ``"bytes=0-499"``), the tuple will
  have ``start=0`` and ``end=499``.

* If no *Range* header is present, an empty list is returned.
* According to RFC 9110 Section 14.2, any *Range* header containing a
  unit other than "bytes" (e.g., ``"seconds=1-2"``) is ignored. These ignored
  headers do not cause the parsing to fail; a list is returned.
* If a *Range* header uses the "bytes" unit but is malformed (e.g.,
  missing the hyphen, containing invalid characters, or invalid numbers),
  the function returns ``None``.
// @snippet qhttpheaders-rangevalues

// @snippet qhttpheaders-setrangevalues
Sets the *Range* HTTP header field to the specified list of ranges (tuples).

The ranges are formatted using the "bytes" unit. For each QHttpHeaderRange in the list:

* A range with only a start (e.g., ``(500, None)`` is formatted as ``"500-"``.
* A range with only an end (e.g., ``(None, 500)``)
  is formatted as ``"-500"``, representing the last 500 bytes.
* A range with both start and end (e.g., ``(0, 499)``)
  is formatted as ``"0-499"``.

If multiple ranges are provided, they will be joined by commas, for example:
``"bytes=0-499, 1000-"``.

If the list is empty, the *Range* header is removed.
// @snippet qhttpheaders-setrangevalues
