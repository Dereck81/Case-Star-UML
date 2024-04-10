#!/usr/bin/python

from modules.functions import _deletekeys, print

class SQLScriptGenerator(object):

	def __init__(self, dict_: dict, idTableColumn: dict) -> None:
		self.dataTable: dict = dict_
		self.keysDataTable: list = list(self.dataTable.keys())
		self.idTableColumn: dict = idTableColumn

	def generateScript(self) -> str:
		self.ListGeneratedTables: dict = dict()
		self.tableDepen: dict = dict()
		self.resultFK: str
		self.currentTable: str
		self.__concatTypeLengthAttribute()
		self.__replaceBooleanAttributeToString()

		for table in self.keysDataTable:
			scriptDB: str = str()
			self.resultFK = str()
			self.currentTable = table
			self.tableDepen.update({table : False})
			scriptDB += f"CREATE TABLE {table} (\n"
			scriptDB += self.__concatAttributesProperties(self.dataTable[table])
			scriptDB += self.resultFK.rstrip(',')+'\n'
			scriptDB += "\n)\nGO"+"\n"*2
			self.ListGeneratedTables.update({table : scriptDB})

		print(f"Cantidad de tablas generadas: {len(self.ListGeneratedTables.keys())}", 2, 1)
		
		ST: list = self.__SortTables()
		scriptDB = ''.join(self.ListGeneratedTables.get(table) for table in ST)

		return scriptDB

	def __concatAttributesProperties(self, listAttributesDict: list) -> str:
		result: str = str()
		# para desactivar el NOT NULL solo remueva de la lista properties el elemente "notNullable"
		#properties: list = ["name", "type_length", "primaryKey", "unique", "nullable"]
		properties: list = ["name", "type_length", "primaryKey", "unique", "nullable", "notNullable"]

		for i, column in enumerate(listAttributesDict):
			result += "\t"
			for p in properties:
				try:
					result += f"{column[p]} "
				except KeyError:
					continue
			self.__addedFK(column)
			result = result.rstrip()
			if len(listAttributesDict) != i+1 :
				result += ','
			elif len(self.resultFK) > 0:
				result += ','
			result += "\n"

		return result.rstrip()
	
	def __concatTypeLengthAttribute(self) -> None:
		for table in self.keysDataTable:
			for i, column in enumerate(self.dataTable[table]):
				type = column.get("type")
				length = column.get("length")
				
				length = length if (length is None) else (None if length == 0 else length)
				
				self.dataTable[table][i] = _deletekeys(self.dataTable[table][i], ["length", "type"])
				
				if type and length:
					self.dataTable[table][i].update({"type_length" : f"{type}({length})"})
				elif not (type is None) and length is None:
					self.dataTable[table][i].update({"type_length" : f"{type}"})

	def __replaceBooleanAttributeToString(self) -> None:
		properties: list = ["primaryKey", "unique", "nullable"]
		replaceBoolToString: dict = {
			"primaryKey"	:	"PRIMARY KEY",
			"unique"		:	"UNIQUE",
			"nullable"		:	"NULL",
			"notNullable"	:	"NOT NULL" 
		}

		for table in self.keysDataTable:
			for i, column in enumerate(self.dataTable[table]):
				
				if not "nullable" in column.keys():
					self.dataTable[table][i].update({"notNullable" : replaceBoolToString["notNullable"]})

				for p in properties:
					try:
						#En starUML una propiedad como PK o U, siempre van a ser True
						#En el caso de que dicho atributo no tenga esa propiedade
						#No existirá dicha propiedad como false, unique:false (No existe)
						if type(column[p]) is bool and column[p]:
								self.dataTable[table][i][p] = replaceBoolToString[p]
					except KeyError:
						continue

	def __addedFK(self, column: dict) -> None:
		if column.get("foreignKey"):
			try:
				nameTableColumn = self.__returnNameTableColumn(column["referenceTo"]["$ref"])
				if nameTableColumn:
					self.resultFK += f"\n\tFOREIGN KEY ({column['name']}) REFERENCES {nameTableColumn[0]}({nameTableColumn[1]}),"
					self.__TableDependency(nameTableColumn[0])

			except Exception:
				return False
		return

	def __returnNameTableColumn(self, idColumna: str = None) -> list:
		'''
		return [nameTable, nameColumn] 
		'''
		for table in self.keysDataTable:
			for column in self.dataTable[table]:
				if column["_id"] == idColumna:
					return [table, column["name"]]
		return list()

	def __TableDependency(self, tableDependency: str) -> None:
		valueTableDepen = self.tableDepen.get(self.currentTable)
		if not type(valueTableDepen) is bool:
			self.tableDepen.update({self.currentTable : valueTableDepen+[tableDependency]})
		else:
			self.tableDepen.update({self.currentTable : [tableDependency]})

	def __SortTables(self) -> list:
		listTablesFalse: list = list()
		listTablesDepen: list = list()
		listTablesDepen_F: list = list()
		del_elements: list = list()
		indx_: list = list()
		i = 0

		for table, vbool in self.tableDepen.items():
			if not type(vbool) is bool:
				listTablesDepen.append(table)
			else:
				listTablesFalse.append(table)

		if not listTablesDepen:
			return listTablesFalse


		for table in listTablesDepen:
			_lstTbReference = self.tableDepen.get(table, [])
			if not any(tb in listTablesDepen for tb in _lstTbReference):
				listTablesDepen_F.append(table)
				del_elements.append(table)
		
		for x in del_elements:
			listTablesDepen.remove(x)
		
		del del_elements

		while(i < len(listTablesDepen_F)):
			_lstTbReference = self.tableDepen.get(listTablesDepen_F[i], [])
			indx_ = list()
			for tb in _lstTbReference:
				if tb in listTablesDepen_F:
					indx_.append(listTablesDepen_F.index(tb))
					
			if indx_:
				for indx in indx_:
					if i < indx:
						listTablesDepen_F.insert(i, listTablesDepen_F[indx])
						listTablesDepen_F.pop(indx+1)
			else:
				i+=1

		return listTablesFalse + listTablesDepen_F + listTablesDepen
