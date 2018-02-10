# coding=UTF-8
import UNBT
from random import randint
import textwrap
import os
import directories

from pymclevel import alphaMaterials, nbt, TAG_Compound, TAG_List, TAG_Int, TAG_Byte_Array, TAG_Short, TAG_Byte, TAG_String, TAG_Double, TAG_Float, TAG_Long

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

inputs = (
	  ("TESTCHEST TE", "label"),
	  ("Select a volume in space.", "label"),
	  ("Fill it with chests.", "label"),
	  ("Cause the problem?",True),
	  ("Run the filter.", "label"),
	  ("Random items should be added to each chest.", "label"),
	  ("adrian@theworldfoundry.com", "label"),
	  ("http://theworldfoundry.com", "label"),
)

def perform(level,box,options):

	# Pre-condition: fill a selection box in MCEdit with south facing Chests (block 54). This filter does not verify the block type and assumes it is a container

	# Add items to the chests
	
	for (chunk, _, _) in level.getChunkSlices(box):
		newTE = []
		for e in chunk.TileEntities: # Loop through all the block entities in this chunk
			x = e["x"].value
			y = e["y"].value
			z = e["z"].value
			if (x,y,z) in box: # Only process the entities within the selection, ignore malformed entries
				# print e["id"],level.blockAt(x,y,z)
				# print fromNative(e)
				if "Items" not in e:
					e["Items"] = TAG_List()
				itemsTag = e["Items"]
				item = TAG_Compound()
				item["id"] = TAG_String(str(randint(0,255)))
				item["Damage"] = TAG_Short(randint(0,127))
				item["Count"] = TAG_Byte(randint(1,64))
				item["Slot"] = TAG_Byte(randint(0,27))
				itemsTag.append(item)
			if options["Cause the problem?"] == True:
				#chunk.TileEntities.remove(e)
				newTE.append(e)
		if options["Cause the problem?"] == True:
			print "Replacing the chunk's TileEntities"
			chunk.TileEntities[:] = newTE
	
	level.markDirtyBox(box)	
	
	# At this point each chest should have an item. Check the console for results
	printEmptyChests(level,box,options)
	
def printEmptyChests(level,box,options):
	for (chunk, _, _) in level.getChunkSlices(box):
		for e in chunk.TileEntities: # Loop through all the block entities in this chunk
			x = e["x"].value
			y = e["y"].value
			z = e["z"].value
			if (x,y,z) in box: # Only process the entities within the selection, ignore malformed entries
				if "Items" in e:
					if len(e["Items"]) == 0:
						print fromNative(e)
				
def fromNative(nativeNBT): # Version specific mapping from supplied NBT format
	# Data transformation, and any validation
	x = nativeNBT["x"].value
	y = nativeNBT["y"].value
	z = nativeNBT["z"].value
	
	if "CustomName" in nativeNBT: customname = nativeNBT["CustomName"].value
	else: customname = ""
	if "Lock" in nativeNBT: lock = nativeNBT["Lock"].value
	else: lock = ""
	items = []	
	if "Items" in nativeNBT:
		undefinedslot = 0

		for item in nativeNBT["Items"]: # JSON?
			print "Parsing Item: ",item
			if "id" in item: item_id = item["id"].value
			else: item_id = ""
			if "Damage" in item: item_damage = item["Damage"].value
			else: item_damage = 0
			if "Slot" in item:
				item_slot = item["Slot"].value
				if item_slot > undefinedslot:
					undefinedslot = item_slot+1 # We don't want to overwrite any existing item slots, so move the cursor for undefined slots past
			else: 
				item_slot = undefinedslot
				undefinedslot += 1
			if "Count" in item: item_count = item["Count"].value
			else: item_count = 1
			item_display_lore_l = []
			item_tag_ench_l = []
			item_display_name = ""
			item_potion = ""
			if "tag" in item:
				item_tag = item["tag"]
				if "display" in item_tag: # compound
					item_display = item_tag["display"]
					if "Name" in item_display: item_display_name = item_display["Name"].value
					if "Lore" in item_display: 
						for lore in item_display["Lore"]:
							item_display_lore_l.append(lore.value)
				if "ench" in item_tag:
					for ench in item_tag["ench"]:
						if "id" in ench: item_tag_ench_id = ench["id"].value
						else: item_tag_ench_id = 0
						if "lvl" in ench: item_tag_ench_lvl = ench["lvl"].value
						else: item_tag_ench_lvl = 0
						item_tag_ench_l.append((item_tag_ench_id,item_tag_ench_lvl))
				if "Potion" in item_tag:
					item_potion = item_tag["Potion"].value
			items.append((item_id,item_damage,item_slot,item_count,item_display_name,item_display_lore_l,item_tag_ench_l,item_potion))
	if "LootTable" in nativeNBT: loottable = nativeNBT["LootTable"].value
	else: loottable = ""
	if "LootTableSeed" in nativeNBT: loottableseed = nativeNBT["LootTableSeed"].value
	else: loottableseed = 0
	
	# Create canonical and return it
	return ((x,y,z),customname,lock,items,loottable,loottableseed)
	