# CS121: PA 7 - Diversity Treemap
#
# Mayarak Quintero
#
# Code for constructing a treemap.

import argparse
import pandas as pd
import sys
import tree
import drawing
import click

###############
#             #
#  Your code  #
#             #
###############


def load_diversity_data(filename, debug=False):
	'''
	Load Silicon Valley diversity data and print summary

	Inputs:
		filename: (string) the name pf the file with the data

	Returns: a pandas dataframe
	'''
	data = pd.read_csv(filename)

	if debug:
		print("Diversity data comes from the following {} companies:".format(len(data.company.unique())),
			  data.company.unique())
		print("The data includes {} employes".format(data['count'].sum()))
		print("""
			#########
			gender
			#########
			""")
		print("female:{}".format((data.groupby('gender')['count'].sum())[0]))
		print("male:{}".format((data.groupby('gender')['count'].sum())[1]))
		print("""
			#########
			race
			#########
			""")
		print("Asian:{}".format((data.groupby('race')['count'].sum())[0]))
		print("Latino:{}".format((data.groupby('race')['count'].sum())[1]))
		print("White:{}".format((data.groupby('race')['count'].sum())[2]))
		print("""
			#########
			job_category
			#########
			""")
		print("Executive/Senior officials & Mgrs:{}".format(
			(data.groupby('job_category')['count'].sum())[0]))
		print("Professionals:{}".format(
			(data.groupby('job_category')['count'].sum())[1]))

		# Add print statements here (if debug is True)

	return data


def compute_internal_counts(t):
	'''
	Assign a count to the interior nodes.  The count of the leaves
	should already be set.  The count of an internal node is the sum
	of the counts of its children.

	Inputs: 
		t (Tree): a tree

	Returns:
		The input tree t should be modified so that every internal node's
		count is set to be the sum of the counts of its children.

		The return value will be:
		- If the tree has no children: the value of the count attribute
		- If the tree has children: the sum of the counts of the children
	'''

	if t.num_children == 0:
		return t.count
	else:
		total_count = 0
		for st in t.children:
			total_count += compute_internal_counts(st)
			t.count = total_count

	return t.count


def compute_verbose_labels(t, prefix=None):
	'''
	Assign a verbose label to non-root nodes. Verbose labels contain the 
	full path to that node through the tree. For example, following the 
	path "Google" --> "female" --> "white" should create the verbose label 
	"Google: female: white". For the root node, the verbose label should be
	an empty string ("").

	Inputs:
		t (Tree): a tree

	Outputs:
		Nothing. The input tree t should be modified to contain
			verbose labels for all nodes
	'''
	if prefix == None:
		t.verbose_label = ""
	elif prefix == "":
		t.verbose_label = t.label
	else:
		t.verbose_label = prefix + ": " + t.label
	if t.num_children:
		for st in t.children:
			compute_verbose_labels(st, t.verbose_label)

	return None


def prune_tree(t, values_to_discard):
	'''
	Returns a tree with any node whose label is in the list values_to_discard
	(and thus all of its children) pruned. This function should return a copy
	of the original tree and should not destructively modify the original tree.
	The pruning step must be recursive.

	Inputs:
		t (Tree): a tree
		values_to_discard (list of strings): A list of strings specifying the
				  labels of nodes to discard

	Returns: a new Tree object representing the pruned tree
	'''
	pruned_tree = tree.Tree(t.label, t.count)
	if t.num_children:
		for st in t.children:
			if st.label not in values_to_discard:
				pruned_tree.add_child(prune_tree(st, values_to_discard))
	
	return pruned_tree


def validate_tuple_param(p, name):
	assert isinstance(p, (list, tuple)) and len(p) == 2 \
		and isinstance(p[0], float) and isinstance(p[1], float), \
		name + " parameter to Rectangle must be a tuple or list of two floats"

	assert p[0] >= 0.0 and p[1] >= 0.0, \
		"Incorrect value for rectangle {}: ({}, {}) ".format(name, p[0], p[1]) + \
		"(both values must be >= 0)"


class Rectangle:
	'''
	Simple class for representing rectangles
	'''

	def __init__(self, origin, size, label, verbose_label):
		# Validate parameters
		validate_tuple_param(origin, "origin")
		validate_tuple_param(origin, "size")
		assert label is not None, "Rectangle label can't be None"
		assert isinstance(label, str), "Rectangle label must be a string"
		assert verbose_label is not None, "Rectangle verbose_label can't be None"
		assert isinstance(
			verbose_label, str), "Rectangle verbose_label must be a string"

		self.x, self.y = origin
		self.width, self.height = size
		self.label = label
		self.verbose_label = verbose_label

	def __str__(self):
		if self.verbose_label is None:
			label = self.label
		else:
			label = self.verbose_label

		return "RECTANGLE {:.4f} {:.4f} {:.4f} {:.4f} {}".format(self.x, self.y,
																 self.width, self.height,
																 label)

	def __repr__(self):
		return str(self)


def compute_rectangles(t, bounding_rec_height=1.0, bounding_rec_width=1.0):
	'''
	Computes the rectangles for drawing a treemap of the provided tree

	Inputs:
		t (Tree): a tree
		bounding_rec_height, bounding_rec_width (floats): the size of
		   the bounding rectangle.

	Returns: a list of Rectangle objects
	'''

	# Do not remove these function calls
	compute_internal_counts(t)
	compute_verbose_labels(t)

	return create_helper(t, 0.0, 0.0, bounding_rec_width, bounding_rec_height, True)

def create_helper(t, x, y, width, height, change):
	'''
	Recursively creates rectangles
	'''

	rectangles_list = []

	if not t.num_children():
		return [Rectangle((x,y), (width, height), t.label, t.verbose_label)]
	for st in t.children:
		if change:
			if t.count == 0:
				width2 = 0
			else:
				weight = st.count / t.count
				width2 = weight * width
			rectangles = create_helper(st, x, y, width2, height, not change)
			x += width2
		else:
			if t.count == 0:
				height2 = 0
			else:
				weight = st.count/t.count
				height2 = weight * height
			rectangles = create_helper(st, x, y, width, height2, not change)
			y += height2 
		rectangles_list += rectangles

	return rectangles_list

#############################
#                           #
#  Our code: DO NOT MODIFY  #
#                           #
#############################

@click.command(name="treemap")
@click.argument('diversity_file', type=click.Path(exists=True))
@click.option('--categories', '-c', type=str)
@click.option('--prune', '-p', type=str)
@click.option('--output', '-o', type=str)
def cmd(diversity_file, categories, prune, output):

	data = load_diversity_data(diversity_file)

	if categories is not None:
		categories = categories.split(",")

	if prune is not None:
		prune = prune.split(",")

	data_tree = tree.data_to_tree(data, categories)

	compute_internal_counts(data_tree)

	compute_verbose_labels(data_tree)

	if prune is not None:
		data_tree = prune_tree(data_tree, prune)

	rectangles = compute_rectangles(data_tree)

	if output == "-":
		for rect in rectangles:
			print(rect)
	else:
		drawing.draw_rectangles(rectangles, output)


if __name__ == "__main__":
	cmd()  # pylint: disable=no-value-for-parameter
