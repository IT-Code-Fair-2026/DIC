# Cultural theme assets

The app's cultural theme shows official flags and (optionally) authorised artwork **only if you add them here**.
Nothing is drawn or imitated in code. This is deliberate: see "Protocols" below.

## Flags (`assets/flags/`)
Add the official artwork, unaltered (do not recolour, crop, stretch, redraw or add effects):

- `aboriginal_flag.svg` or `aboriginal_flag.png`
- `torres_strait_islander_flag.svg` or `torres_strait_islander_flag.png`

Get them from the official sources: the National Indigenous Australians Agency (NIAA) publishes the Aboriginal
flag artwork and usage guidelines, and the Torres Strait Regional Authority (TSRA) / Torres Strait Islander
Regional Council publish the Torres Strait Islander flag. Read the current usage guidelines before use and
show the flags respectfully (never on the floor of a page, behind text, or as decoration in patterns).

## Artwork (`assets/artwork/`)
Only add artwork you have **written permission** to use from the artist or their community.
The app shows an image from this folder only when `assets/artwork/attribution.txt` also exists. Put in that file, as
the text to display, the artist's name, their community / language group, the artwork title, and that permission
was given (for example: "Artwork: 'Title' by Artist Name, Community. Used with permission.").

## Protocols
- Traditional and contemporary Aboriginal and Torres Strait Islander art, patterns and designs are Indigenous
  Cultural and Intellectual Property (ICIP). Do not generate, copy or imitate "Aboriginal style" dot painting, X-ray
  art, cross-hatching, or Torres Strait Islander designs.
- Follow "Protocols for using First Nations Cultural and Intellectual Property in the Arts" (Australia Council for the
  Arts) and the AIATSIS Code of Ethics for Aboriginal and Torres Strait Islander Research.
- Where possible, ask your university's Indigenous unit or a local community organisation to review the design.
- Edit `ACK_TEXT` in `app.py` to name the local Traditional Custodians.
