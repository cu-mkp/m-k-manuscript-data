for $lang in //(la | de | el | it | oc | po)
let $lang-name := $lang/local-name()
let $entry := $lang/ancestor::div[@id]
let $id := $entry/@id
let $categories := $entry/@categories
let $head := $entry/head
let $parent1 := $lang/parent::*/local-name()
let $parent2 := $lang/parent::*/parent::*/local-name()
let $parent3 := $lang/parent::*/parent::*/parent::*/local-name()
return
concat($id,':',$lang-name,':',normalize-space($head),':',$categories,':',$parent3,':',$parent2,':',$parent1,':',normalize-space($lang),'&#10;')