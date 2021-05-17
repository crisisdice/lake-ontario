from io import BytesIO
from numpy import array, copy, frombuffer, reshape
from scipy.io import loadmat, savemat
from scipy.sparse import csr_matrix

import psycopg2
import os

class MatrixStore:
	def __init__(self, settings, remote):
		self.shape = (settings["dim"], settings["dim"])
		self.steps = settings["steps"]
		self.seasons = settings["seasons"]
		self.template = lambda season, power : f"{season}:{power}"

	def seed(self):
		self.create_table()

		file_name = lambda season : f'data/{season}.mat'

		for season in self.seasons:
			transition_matrix = array(loadmat(file_name(season))['M'])
			multiplicand = copy(transition_matrix)
			self.store(transition_matrix, season, 1)
			
			for power in range(2, self.steps):
				result = csr_matrix(transition_matrix) * csr_matrix(multiplicand)
				self.store(result.toarray(), season, power)
				multiplicand = result

	def get_connection(self):
		return psycopg2.connect(
			port=5433,
			database="suppliers",
			user="postgres",
			password="Hall0W3lt!")

	def store(self, array, season, power):
		command = "INSERT INTO seasons(season_id, matrix) VALUES(%s, %s);"
		key = self.template(season, power)
		stream = BytesIO()
		savemat(stream, { 'M': array }, do_compression=True)
		stream.seek(0)
		data = stream.read()
		conn = None
		try:
			conn = self.get_connection()
			cur = conn.cursor()
			cur.execute(command, (key, data))
			cur.close()
			conn.commit()
		except (Exception, psycopg2.DatabaseError) as error:
			raise
		finally:
			if conn is not None:
				conn.close()

	def retrieve(self, season, power):
		command = "SELECT matrix FROM seasons WHERE season_id = %s;"
		key = self.template(season, power)
		conn = None
		try:
			conn = self.get_connection()
			cur = conn.cursor()
			cur.execute(command, (key,))
			mview = cur.fetchone()
			cur.close()
			return array(loadmat(BytesIO(bytes(mview[0])))['M'])
		except (Exception, psycopg2.DatabaseError) as error:
			raise
		finally:
			if conn is not None:
				conn.close()

	def create_table(self):
		conn = None
		command = "CREATE TABLE seasons (season_id VARCHAR(10) PRIMARY KEY, matrix bytea NOT NULL)"
		try:
			conn = self.get_connection()
			cur = conn.cursor()
			cur.execute(command)
			cur.close()
			conn.commit()
		except (Exception, psycopg2.DatabaseError) as error:
			raise
		finally:
			if conn is not None:
				conn.close()

