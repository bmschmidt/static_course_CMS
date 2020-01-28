import Text.Pandoc.JSON

main = toJSONFilter compactifyList

compactifyList :: Block -> Block
compactifyList blk = case blk of
  (BulletList items)         -> BulletList $ map compactifyItem items
  (OrderedList attrbs items) -> OrderedList attrbs $ map compactifyItem items
  _                          -> blk

compactifyItem :: [Block] -> [Block]
compactifyItem [Para bs] = [Plain bs]
compactifyItem item      = item
