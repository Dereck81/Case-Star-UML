#!/usr/bin/python
#

from modules.functions import _deletekeys, print

class StarUMLinterpreter(object):

	def __init__(self, data: dict) -> None:
		self.data_json: dict = data
		self.project_MDJ: dict

		self.tables_columns: dict
		self.ERD_diagram_view_id_columns: dict

		self.ERD_data_models: list
		self.ERD_diagrams: list
		self.ERD_entities: list
		self.IDS_ERD_diagram_view: list
		
		self.ERD_data_model_select: int
		self.ERD_diagram_select: int
	
	def get_tables_columns(self, index_data_model: int, index_diagram: int) -> list:
		self.ERD_data_model_select = index_data_model
		self.ERD_diagram_select = index_diagram

		self.__interpret_MDJ()
		self.__interpret_data_model()
		self.__interpret_diagram()
		self.__filter_tables_columns_views()
		self.__interpret_ERD_entity()

		if self.__interpret_tables_columns():
			return [self.tables_columns, self.ERD_diagram_view_id_columns]
		
		return list()
	
	def get_data_model(self) -> list: 
		self.__interpret_MDJ()
		if self.__interpret_data_model(): return self.ERD_data_models
		return list()
	
	def get_diagrams(self, index_data_model: int) -> list:
		self.ERD_data_model_select = index_data_model
		self.__interpret_MDJ()
		self.__interpret_data_model()
		if self.__interpret_diagram(): return self.ERD_diagrams
		return list()

	def __interpret_MDJ(self) -> bool:
		if self.data_json["_type"] != "Project":
			print("Proyect not found.", 2, 2)
			return False
		
		self.project_MDJ = self.data_json
		return True
		
	def __interpret_data_model(self) -> bool:
		if not self.project_MDJ: return False

		self.ERD_data_models = list(
			filter(
				lambda x: x["_type"] == "ERDDataModel", 
				self.project_MDJ["ownedElements"]
			)
		)
		
		if len(self.ERD_data_models) == 0:
			print("No data model found.", 2, 2)
			return False
	
		return True

	def __interpret_diagram(self) -> bool:
		if len(self.ERD_data_models) == 0: return False
		self.ERD_diagrams = list(
			filter(
				lambda x: x["_type"] == "ERDDiagram",
				self.ERD_data_models[self.ERD_data_model_select]["ownedElements"]
			)
		)

		if len(self.ERD_diagrams[0]) == 0:
			print("No diagram found.", 2, 2)
			return False

		return True

	def __interpret_ERD_entity(self) -> bool:
		if len(self.ERD_diagrams[0]) == 0: return False

		self.ERD_entities = list(
			filter(
				lambda x: x["_type"] == "ERDEntity",
				self.ERD_data_models[self.ERD_data_model_select]["ownedElements"]
			)
		)

		if len(self.ERD_entities) == 0: return False

		return True


	def __filter_tables_columns_views(self):
		self.ERD_diagram_view_id_columns = dict()

		temp: list = list()
		temp_sub_views: list = list()

		self.IDS_ERD_diagram_view = list(
			filter(
				lambda x: x["_type"] == "ERDEntityView",
				[y for y in  self.ERD_diagrams[self.ERD_diagram_select]["ownedViews"]]
			)
		)

		for x in self.IDS_ERD_diagram_view:
			try:
				temp.append(x["model"]["$ref"])

				for y in x["subViews"]:
					if y["_type"] == "ERDColumnCompartmentView":
						for z in y["subViews"]:
							if not "visible" in list(z.keys()) or z["visible"]:
								temp_sub_views.append(z["model"]["$ref"])
								
				self.ERD_diagram_view_id_columns.update({f"{x['model']['$ref']}": temp_sub_views})
				temp_sub_views = list()
			except KeyError: continue

		self.IDS_ERD_diagram_view = temp

	def __interpret_tables_columns(self):
		temporary_columns: list
		self.tables_columns = dict()

		if len(self.ERD_entities) == 0: return False

		for table in self.ERD_entities:
			temporary_columns = list()

			try:
				if table["_id"] in self.IDS_ERD_diagram_view:
					for columns in table["columns"]:
						if columns["_id"] in self.ERD_diagram_view_id_columns[table["_id"]]:
							temporary_columns.append(_deletekeys(columns))
					if len(temporary_columns) > 0: 
						self.tables_columns.update({f"{table['name']}": temporary_columns})
			except KeyError: continue

		if len(self.tables_columns) == 0: return False

		return True
