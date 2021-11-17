# Updating the Schema in oXygen XML Editor

## Edit the schema
1. Open `.rng` version of schema in oXygen
2. Update these "manually" (i.e., add or remove sections, elements, attributes, etc. by hand)

## Generate the `.rnc` version
1. Under `Tools`, select `Generate/convert schema`
2. In the pop-up window:
> - Input = relax ng xml (browse to "rng schema" file)
> - Output = rng compact (i.e., `rnc`) (browse to that option)
> - Leave all other settings/options as is

## Generate a "reading" version (markdown)
1. "Save as" the `.rnc` document
2. The popup window will automatically save as `.rnc`, so need to change this
3. Manually change the file extension to `.md`
