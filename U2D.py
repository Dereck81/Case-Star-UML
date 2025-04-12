#!/usr/bin/python
# Support program StarUML
# Version: 6.0.1

from modules.functions import print, save_file
from modules.SQLScriptGenerator import SQLScriptGenerator
from modules.StarUMLinterpreter import StarUMLinterpreter
from modules.config import Config
import json, argparse

parse = argparse.ArgumentParser(
	description=
	"""
	\rU2D (UML to Database) script that interprets a StarUML .mdj diagram into a SQL file.

	\rNote 1:
	\rThis script only transforms the diagram into a .sql file, but does not modify the attributes or data types. 
	\rConsider the database you will be using it for and carefully specify the data types, etc.

	\rNote 2: 
	\rUse Delete from Model instead of Delete in StarUML, as some entities may remain in the diagram 
	\rand appear when generating it.""",  
	formatter_class=argparse.RawTextHelpFormatter
)

parse.add_argument("file", type=str, help="path to the .mdj file")
parse.add_argument('-dm', '--data-model', metavar='', type=int, help="the number of the data model to select")
parse.add_argument("-d", "--diagram", metavar='', type=int, help="the number of the diagram to select")
parse.add_argument("-o", "--output", metavar='', type=str, help="output file name, if not specified, the default name will be 'script.sql'")
parse.add_argument("-v", "--verbose", action="store_true", help="displays detailed information about the conversion process")

args = parse.parse_args()

class U2D(object):

	def __init__(self, path_file: str) -> None:
		self.data_json: dict
		self.banner()
		self.read_file(path_file)
		self.interpreter = StarUMLinterpreter(self.data_json)


	def banner(self) -> None:
		print("""

		░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓███████▓▒░  
		░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
		░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
		░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
		░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
		░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
		 ░▒▓██████▓▒░░▒▓████████▓▒░▒▓███████▓▒░  
		
			Created by Dereck81
		""")

	def read_file(self, pathFile: str) -> bool:
		print("Reading file... ", 2, 1, end='')
		try:
			with open(pathFile, encoding="UTF-8") as dataFile:
				self.data_json = json.load(dataFile)
			print("Ok", 1, 4)
			return True
		except Exception as e:
			print("ERROR!", 1, 2)
			print(e, 2)
			exit(1)
	
	def show_data_models(self) -> None:
		print("Data Models: ", 2)
		data_models: list = self.interpreter.get_data_model()
		for i, data_model in enumerate(data_models):
			print(f"{i}) {data_model['name']}", 2, 1) 

	def show_diagrams(self, index_data_model: int) -> None:
		data_models: list = self.interpreter.get_data_model()
		print(f"Selected Data Model: {data_models[index_data_model]['name']}", 2)
		print("Diagrams: ", 2)
		diagrams: list = self.interpreter.get_diagrams(index_data_model)
		for i, diagram in enumerate(diagrams):
			print(f"{i}) {diagram['name']}", 2, 1) 
		

	def generate(self, index_data_model: int, index_diagram: int, output_file: str) -> None:
		print("Getting tables and columns...", 2)
		table_columns_id: list = self.interpreter.get_tables_columns(index_data_model, index_diagram)
		table_columns, ID_table_columns = table_columns_id

		print("Generating SQL code...", 2)
		SQLGenerator: SQLScriptGenerator = SQLScriptGenerator(table_columns, ID_table_columns)
		script: str = SQLGenerator.generate_script()

		print(f"Saving generated SQL code in '{output_file if output_file is not None else 'script.sql'}'", 2, 4)
		save_file(script, output_file if output_file is not None else "script.sql")
		print("Finished process!", 2, 4)

	


if __name__ == "__main__":
	run = U2D(args.file)
	Config.verbose = args.verbose

	if args.data_model is not None and args.diagram is not None:
		run.generate(args.data_model, args.diagram, args.output)
	elif args.data_model is None:
		run.show_data_models()
	elif args.diagram is None: 
		run.show_diagrams(args.data_model)