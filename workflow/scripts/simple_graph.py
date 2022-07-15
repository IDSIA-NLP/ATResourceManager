#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: ...
Author: ...
Month Year
"""

class SimpleGraph:
    def __init__(self, egdes):
        self.egdes = egdes
        self.graph_dict = {}
        
        for parent, child in self.egdes:
            if parent in self.graph_dict:
                self.graph_dict[parent].append(child)
            else:
                self.graph_dict[parent] = [child]
                
                
    def get_paths(self, parent, child, path=[]):
        path = path + [parent]
        
        if parent == child:
            return [path]
        
        if parent not in self.graph_dict:
            return []
        
        paths = []
        for node in self.graph_dict[parent]:
            if node not in path:
                new_paths = self.get_paths(node, child, path)
                for p in new_paths:
                    paths.append(p)
        
        return paths
    
    def get_children(self, parent, children=[]):
        children = children + [parent]
        
        if parent not in self.graph_dict:
            #print("empty")
            return children
        
        all_children = []
        for node in self.graph_dict[parent]:
            #print("in child: ", node)
            if node not in children:
                #print("not in children | ", node)
                new_children = self.get_children(node, children)
                for c in new_children:
                    #print("new child: ", c)
                    all_children.append(c)
        
        return list(set(all_children))
