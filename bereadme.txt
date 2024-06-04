
# Hierarchy
	The Objects tab in C4D contains a hierarchy of objects, in what looks like a binary tree
	
	Animation 'tracks' can be associated with the transform attributes of each node in the tree
	
	When an animator copies a hierarchy to a new one the target is identical to the source in all ways except the animation tracks
	
	The omission of the tracks is a major issue for animators
	
	This plugin navigates the binary tree and copies the animation tracks to the target
	
	Nodes are matched by name, which raises potential problems
	
		 Duplicate names
		 
		 Changed names in the target
		 
		 New nodes in the target
		 
		 Moved nodes in the target
		 
		 Deletions in the target

    Processing
	
		navigate the tree
		
		for each node
		
			if has animation tracks
		
				using the full name of the node, i.e. using each of the higher node names
			
				find the same full name in the target, ignoring entries which have already been processed
			
				if found	
			
					copy over tracks from the source
					
					add this target full node name to a processed list, so we don't target it again
					
				else
				
					remove the highest level name and try again, this allows for rename or move of the highest level
					
					keep removing high level names until only the node name is left, in which case we are doing a match solely by name
					
					note that we are ignoring target nodes that have been processed already
					
					