(: This XQuery script selects elements "la", "de", "el", "it", "oc", "po" in the document, and returns information about them :)
(: This information includes the id of the ancestor div element, the local name of the current element, the text content of the :)
(: ancestor head element, the categories attribute of the ancestor div element, and the local names of the current element's parent elements :)

(: Select all the "la", "de", "el", "it", "oc", "po" elements in the document :)
for $lang in //(la | de | el | it | oc | po)
  
  (: Get the local name of the current element :)
  let $lang-name := $lang/local-name()
  
  (: Get the ancestor div element of the current element and its id and categories attributes :)
  let $entry := $lang/ancestor::div[@id]
  let $id := $entry/@id
  let $categories := $entry/@categories
  
  (: Get the ancestor head element of the ancestor div element and its text content :)
  let $head := $entry/head
  
  (: Get the local names of the current element's parent elements :)
  let $parent1 := $lang/parent::*/local-name()
  let $parent2 := $lang/parent::*/parent::*/local-name()
  let $parent3 := $lang/parent::*/parent::*/parent::*/local-name()
  
  (: Concatenate all the information and return it as a string with line break at the end :)
  return concat($id,':',$lang-name,':',normalize-space($head),':',$categories,':',$parent3,':',$parent2,':',$parent1,':','"',normalize-space($lang),'"','&#10;')
