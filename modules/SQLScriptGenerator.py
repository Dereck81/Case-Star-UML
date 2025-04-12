#!/usr/bin/python

from modules.functions import _deletekeys, print
from colorama import Fore, init, Fore, Style
from collections import defaultdict, deque
from modules.config import Config

init(autoreset=True)
class SQLScriptGenerator(object):

	def __init__(self, dict_: dict, id_table_column: dict) -> None:
		self.data_table: dict = dict_
		self.keys_data_table: list = list(self.data_table.keys())
		self.id_table_column: dict = id_table_column

		self.generated_tables: dict
		self.table_dependency: dict
		self.result_FK: str
		self.current_table: str

	def generate_script(self) -> str:
		self.generated_tables: dict = dict()
		self.table_dependency: dict = dict()

		self.__concat_type_length_attribute()
		self.__replace_boolean_attribute_to_string()

		for table in self.keys_data_table:
			script: str = str()

			self.result_FK = str()
			self.current_table = table
			self.table_dependency.update({table : False})

			if Config.verbose: print(f"Generating table: {table}", 2, 4)

			script += f"CREATE TABLE {table} (\n"
			script += self.__concat_attributes_properties(self.data_table[table])
			script += self.result_FK.rstrip(',')+'\n'
			script += "\n);\n"+"\n"*2

			self.generated_tables.update({table : script})

		print(f"Number of tables generated: {len(self.generated_tables)}", 2, 4)
		
		sort_tables: list = self.__sort_tables()
		script = ''.join(self.generated_tables.get(table) for table in sort_tables)

		return script

	def __concat_attributes_properties(self, attributes: list) -> str:
		result: str = str()
		properties: list = ["name", "type_length", "primaryKey", "unique", "nullable", "notNullable"]
		# To disable NOT NULL, simply remove the "notNullable" element from the properties list.	
		# Example: properties: list = ["name", "type_length", "primaryKey", "unique", "nullable"]

		for i, column in enumerate(attributes):
			result += "\t"

			if Config.verbose: print(f"Generating table attribute ({self.current_table}): {column['name']}", 2)

			for p in properties:
				try: result += f"{column[p]} "
				except KeyError: continue

			self.__added_FK(column)
			result = result.rstrip()

			if len(attributes) != i+1 or len(self.result_FK) > 0 : result += ','

			result += "\n"

		return result.rstrip()
	
	def __concat_type_length_attribute(self) -> None:
		for table in self.keys_data_table:

			for i, column in enumerate(self.data_table[table]):
				type = column.get("type")
				length = column.get("length")

				length = length if (length is not None and length != 0) else None
				
				self.data_table[table][i] = _deletekeys(self.data_table[table][i], ["length", "type"])
				
				if type and length:
					self.data_table[table][i].update({"type_length" : f"{type}({length})"})
				elif type is not None:
					self.data_table[table][i].update({"type_length" : f"{type}"})

	def __replace_boolean_attribute_to_string(self) -> None:
		properties: list = ["primaryKey", "unique", "nullable"]
		replace_bool_to_string: dict = {
			"primaryKey"	:	"PRIMARY KEY",
			"unique"		:	"UNIQUE",
			"nullable"		:	"NULL",
			"notNullable"	:	"NOT NULL" 
		}

		for table in self.keys_data_table:
			for i, column in enumerate(self.data_table[table]):
				
				if not "nullable" in column.keys():
					self.data_table[table][i].update({"notNullable" : replace_bool_to_string["notNullable"]})

				for p in properties:
					try:
						if type(column[p]) is bool and column[p]: 
							self.data_table[table][i][p] = replace_bool_to_string[p]
					except KeyError: continue

	def __added_FK(self, column: dict) -> None:
		if column.get("foreignKey"):
			try:
				name_table_column = self.__return_name_table_column(column["referenceTo"]["$ref"])

				if name_table_column:
					if Config.verbose: print(f"{Fore.LIGHTCYAN_EX}(Foreign Key){Style.RESET_ALL} Dependency found with table: {name_table_column[0]}({name_table_column[1]})", 2)
					self.result_FK += f"\n\tFOREIGN KEY ({column['name']}) REFERENCES {name_table_column[0]}({name_table_column[1]}),"
					self.__table_dependency(name_table_column[0])
					
			except Exception: return False

		return

	def __return_name_table_column(self, id_column: str = None) -> list:
		'''
		return [nameTable, nameColumn] 
		'''
		for table in self.keys_data_table:
			for column in self.data_table[table]:
				if column["_id"] == id_column: return [table, column["name"]]

		return list()

	def __table_dependency(self, table_dependency: str) -> None:
		value_table_dependency = self.table_dependency.get(self.current_table)

		if not type(value_table_dependency) is bool:
			self.table_dependency.update({self.current_table : value_table_dependency+[table_dependency]})
		else:
			self.table_dependency.update({self.current_table : [table_dependency]})


	def __sort_tables(self) -> list:
		print("Reordering tables...", 2)

		graph: dict = {table: dependency if dependency else [] for table, dependency in self.table_dependency.items()}
		order: list = list()

		number_of_dependencies: defaultdict = defaultdict(int)
		
		for table, dependecies in graph.items():
			number_of_dependencies[table] = len(dependecies)
		
		for table in graph:
			number_of_dependencies.setdefault(table, 0)

		queue: deque = deque([table for table in graph if number_of_dependencies[table] == 0])
		
		while queue:
			current: str = queue.popleft()
			order.append(current)
			for table in graph:
				if current in graph[table]:
					number_of_dependencies[table] -= 1
					if number_of_dependencies[table] == 0:
						queue.append(table)
		
		if len(order) != len(graph):
			print("A circular reference was detected, it may not have been sorted correctly.", 2, 3)
			print(f"Only tables that do not have circular dependencies will be generated, {Fore.GREEN}number of tables to generate: {len(order)}{Style.RESET_ALL}", 2, 3)

		return order
		
