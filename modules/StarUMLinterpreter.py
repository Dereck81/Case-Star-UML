#!/usr/bin/python
#

from modules.functions import _deletekeys, print

class StarUMLinterpreter(object):

	def __init__(self, data: dict) -> None:
		self.dataJson: dict = data
	
	def getTablesColumns(self, indexDataModel: int, indexDiagram: int) -> list:
		self.listERDDataModelSelect: int = indexDataModel
		self.listERDDiagramSelect: int = indexDiagram
		self.__interpretMDJ()
		self.__interpretDataModel()
		self.__interpretDiagram()
		self.__filterTablesColumnsViews()
		self.__interpretERDEntity()
		if self.__interpretTablesColumns():
			return [self.tablesColumns, self.listID_ERDDiagramView_IDColumns]
		return list()

	def getDataModel_Diagrams(self) -> list:
		self.__interpretMDJ()
		self.__interpretDataModel()
		if self.__interpretDiagram():
			return [self.listERDDataModel, self.listERDDiagram]
		return list()

	def __interpretMDJ(self) -> bool:
		self.projectMDJ: dict

		if (self.dataJson["_type"] != "Project"):
			print("Proyecto no encontrado!", 2, 2)
			return False
		
		self.projectMDJ = self.dataJson
		return True
		
	def __interpretDataModel(self) -> bool:
		self.listERDDataModel: list

		if not self.projectMDJ:
			return False

		self.listERDDataModel = list(
			filter(
				lambda x: x["_type"] == "ERDDataModel", 
				self.projectMDJ["ownedElements"]
				)
			)
		
		if len(self.listERDDataModel) == 0:
			print("No se encontró ningun ERDDataModel (\"Data Model#\")", 2, 2)
			return False
	
		return True

	def __interpretDiagram(self) -> bool:
		self.listERDDiagram: list

		if len(self.listERDDataModel) == 0:
			return False

		self.listERDDiagram = list(
			filter(
				lambda x: x[0]["_type"] == "ERDDiagram",
				[DM_i["ownedElements"] for DM_i in self.listERDDataModel]
			)
		)

		if len(self.listERDDiagram[0]) == 0:
			print("No se encontró ningun ERDDiagram (\"Diagrama ERD\")", 2, 2)
			return False

		return True

	def __interpretERDEntity(self) -> bool:
		self.listERDEntity: list

		if len(self.listERDDiagram[0]) == 0:
			return False

		self.listERDEntity = list(
			filter(
				lambda x: x["_type"] == "ERDEntity",
				self.listERDDataModel[self.listERDDataModelSelect]["ownedElements"]
			)
		)

		if len(self.listERDEntity) == 0:
			return False

		return True


	def __filterTablesColumnsViews(self):
		self.listID_ERDDiagramView: list
		self.listID_ERDDiagramView_IDColumns: dict = dict()
		temp: list = list()
		temp_subViews: list = list()

		self.listID_ERDDiagramView = list(
			filter(
				lambda x: x["_type"] == "ERDEntityView",
				[y for y in 
	 			self.listERDDiagram[self.listERDDataModelSelect][self.listERDDiagramSelect]["ownedViews"]
				]
			)
		)

		for x in self.listID_ERDDiagramView:
			try:
				temp.append(x["model"]["$ref"])
				for y in x["subViews"]:
					if y["_type"] == "ERDColumnCompartmentView":
						for z in y["subViews"]:
							if not "visible" in list(z.keys()) or z["visible"]:
								temp_subViews.append(z["model"]["$ref"])
				self.listID_ERDDiagramView_IDColumns.update({f"{x['model']['$ref']}": temp_subViews})
				temp_subViews = list()
			except KeyError:
				continue

		self.listID_ERDDiagramView = temp

	def __interpretTablesColumns(self):
		self.tablesColumns: dict = dict()
		columnsTemporal: list = list()

		if len(self.listERDEntity) == 0:
			return False

		for table in self.listERDEntity:
			try:
				if table["_id"] in self.listID_ERDDiagramView:
					for columns in table["columns"]:
						if columns["_id"] in self.listID_ERDDiagramView_IDColumns[table["_id"]]:
							columnsTemporal.append(_deletekeys(columns))
					if len(columnsTemporal) > 0:
						self.tablesColumns.update({f"{table['name']}": columnsTemporal})
			except KeyError:
				continue
			columnsTemporal = list()

		if len(self.tablesColumns) == 0:
			return False

		return True
