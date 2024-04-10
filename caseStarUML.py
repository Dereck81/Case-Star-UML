#!/usr/bin/python
# Support program StarUML
# Version: 6.0.1

from modules.functions import print
from modules.SQLScriptGenerator import SQLScriptGenerator
from modules.StarUMLinterpreter import StarUMLinterpreter
import json

class Case(object):

	def __init__(self) -> None:
		self.dataJson: dict
		
	def readFile(self, pathFile: str) -> bool:
		print("Leyendo archivo... ", 2, 1, end='')
		try:
			with open(pathFile, encoding="UTF-8") as dataFile:
				self.dataJson = json.load(dataFile)
			print("OK!", 1, 4)
			return True
		except Exception as e:
			print("ERROR!", 1, 2)
			print(e, 2)
			return False
		
	def saveFile(self, scriptDB):
		fp = open("ScriptDB.sql", 'w', encoding='UTF-8')
		fp.write("/* Generate code by: caseStarUML.py*/\n\n"+scriptDB)
		fp.close()

	def menuSelectionERD(self):
		listERDDataModelSelect: int = 0
		listERDDiagramSelect: int = 0
		listERDDataModel: list
		listERDDiagram: list
		
		print("""
		.▄▄ · ▄▄▄▄▄ ▄▄▄· ▄▄▄  ▄• ▄▌• ▌ ▄ ·. ▄▄▌       ▄▄·  ▄▄▄· .▄▄ · ▄▄▄ .
		▐█ ▀. •██  ▐█ ▀█ ▀▄ █·█▪██▌·██ ▐███▪██•      ▐█ ▌▪▐█ ▀█ ▐█ ▀. ▀▄.▀·
		▄▀▀▀█▄ ▐█.▪▄█▀▀█ ▐▀▀▄ █▌▐█▌▐█ ▌▐▌▐█·██▪      ██ ▄▄▄█▀▀█ ▄▀▀▀█▄▐▀▀▪▄
		▐█▄▪▐█ ▐█▌·▐█ ▪▐▌▐█•█▌▐█▄█▌██ ██▌▐█▌▐█▌▐▌    ▐███▌▐█ ▪▐▌▐█▄▪▐█▐█▄▄▌
		 ▀▀▀▀  ▀▀▀  ▀  ▀ .▀  ▀ ▀▀▀ ▀▀  █▪▀▀▀.▀▀▀     ·▀▀▀  ▀  ▀  ▀▀▀▀  ▀▀▀ 
		""")
		
		print("Ingrese la ubicacion de su archivo: ", 2, 1, end='')
		filep = input()
		if not self.readFile(filep):
			return
		starUML_I = StarUMLinterpreter(self.dataJson)
		DataModel_Diagrams: list = starUML_I.getDataModel_Diagrams()
		if len(DataModel_Diagrams) == 0:
			print("No se encontró ningun modelo y diagrama!", 2, 2)
			return
		listERDDataModel, listERDDiagram = DataModel_Diagrams
		print("Data Models: ", 2)
		for i, dataModel in enumerate(listERDDataModel, 1):
			print(f"{i}) {dataModel['name']}", 2, 1)
		listERDDataModelSelect = int(input(f"[>] Data model [1- {i}]: "))-1
		for i, diagram in enumerate(listERDDiagram, 1):
			print(f"{i}) {diagram[0]['name']}", 2, 1)
		listERDDiagramSelect = int(input(f"[>] Diagram model [1 - {i}]: "))-1
		tableColumns_ID: list = starUML_I.getTablesColumns(listERDDataModelSelect, listERDDiagramSelect)
		if len(DataModel_Diagrams) == 0:
			print("No se encontró ninguna tabla o columnas!", 2, 2)
			return
		tableColumns, IDtableColumns = tableColumns_ID
		SQLGenerator: SQLScriptGenerator = SQLScriptGenerator(tableColumns, tableColumns_ID)
		self.saveFile(SQLGenerator.generateScript())
		print("Terminado!", 2, 4)


run = Case()
run.menuSelectionERD()

