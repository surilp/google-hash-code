from __future__ import annotations
from typing import Set
from collections import defaultdict
from heapq import heapify, heappop, heappush
import os

'''
coarse matrix
0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 
0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 
0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 
1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 
1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 
1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 
0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 
1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 
'''


class Client:

    def __init__(self, like: Set[str], dislike: Set[str]):
        self.likes = like
        self.dislikes = dislike

    def is_compatible_with(self, other: Client):
        return self.likes.isdisjoint(other.dislikes) and self.dislikes.isdisjoint(other.likes)

    def __str__(self):
        return f'likes = {self.likes}, dislikes = {self.dislikes}'

    def __repr__(self):
        return self.__str__()


class Graph:

    def __init__(self, adj_list, indegree):
        self.adj_list = adj_list
        self.indegree = indegree
        self.active_vertices = [True] * len(self.adj_list)

    def find_maximal_cliques(self):
        vertices = {idx for idx, v in enumerate(self.active_vertices) if v}
        result = []
        self._bron_kerbosch_algo(set(), vertices, set(), result)
        result.sort(key=lambda x: len(x), reverse=False)
        return result

    def _bron_kerbosch_algo(self, current, candidate, exclusion, result):
        if not candidate and not exclusion:
            result.append(current)
            return
        while candidate:
            vertex = candidate.pop()
            self._bron_kerbosch_algo(current.union({vertex}), candidate.intersection(self.adj_list[vertex]),
                                     exclusion.intersection(self.adj_list[vertex]), result)
            exclusion.update({vertex})

    def inactivate_vertices(self, vertices):
        for vertex in vertices:
            self.active_vertices[vertex] = False

    def find_compatible_cliques(self):
        result = []
        maximal_incompatible_cliques = self.find_maximal_cliques()
        while maximal_incompatible_cliques[0] != set():
            print(f'find compatible cliques process left {len(maximal_incompatible_cliques)}')
            current_clique = maximal_incompatible_cliques.pop()
            result.append(current_clique)
            self.inactivate_vertices(current_clique)
            maximal_incompatible_cliques = self.find_maximal_cliques()
        return self.find_max_compatible_vertex(result)

    def find_max_compatible_vertex(self, compatible_cliques):
        print(f'start of find max compatible vertex')
        result = [set()]
        self._helper(compatible_cliques, result, set(), 0)
        return result

    def _helper(self, cliques, result, ds, current):
        if current == len(cliques):
            if len(ds) > len(result[0]):
                while result:
                    result.pop()
                result.append(ds.copy())
            elif len(ds) == len(result[0]):
                result.append(ds.copy())
            print(f'current max result {len(result[0])}')
            return
        for vertex in cliques[current]:
            if ds.isdisjoint(self.adj_list[vertex]):
                ds.add(vertex)
                self._helper(cliques, result, ds, current + 1)
                ds.remove(vertex)
            else:
                self._helper(cliques, result, ds, current + 1)

    def find_max_compatible_vertex_v2(self):
        priority_q = []
        visited = [False] * len(self.adj_list)
        result = set()
        for vertex, indegree in enumerate(self.indegree):
            heappush(priority_q, (indegree, vertex))
        while priority_q:
            degree, vertex = heappop(priority_q)
            if visited[vertex]:
                continue
            result.add(vertex)
            visited[vertex] = True
            for adj_vertex in self.adj_list[vertex]:
                visited[adj_vertex] = True
                for adj_vertex_adj in self.adj_list[adj_vertex]:
                    if self.indegree[adj_vertex_adj] > 1:
                        self.indegree[adj_vertex_adj] -= 1
                        heappush(priority_q, (self.indegree[adj_vertex_adj], adj_vertex_adj))
        return result


class OnePizza:

    def __init__(self, file_name):
        self.clients = self.get_clients(self.parser(file_name))
        self.incompatible_graph = Graph(*self.build_incompatible_client_graph())
        self.file_name = file_name

    def final_result(self):
        compatible_clients = self.get_max_compatible_clients()
        compatible_clients_ingredients = self.get_max_compatible_clients_ingredients(compatible_clients)
        result = len(compatible_clients_ingredients), compatible_clients_ingredients
        print('-' * 50)
        print(self.file_name)
        print(f'total compatible customers - {len(compatible_clients)}')
        print(result)
        print('-' * 50)
        self.result_file_creator(self.file_name, result)

    def result_file_creator(self, file_name, result):
        base, file = os.path.split(file_name)
        file = file.replace('in', 'out')
        with open(os.path.join(base, file), 'w+') as file:
            file.write(f'{result[0]} {" ".join(result[1])}')

    def get_clients(self, data):
        clients = []
        for idx in range(2, len(data), 2):
            dislikes = set(data[idx][1:])
            likes = set(data[idx - 1][1:])
            clients.append(Client(likes, dislikes))
        return clients

    def build_incompatible_client_graph(self):
        adj_list = [set() for _ in range(len(self.clients))]
        adj_matrix = [[0] * len(self.clients) for _ in range(len(self.clients))]
        indegree = [0] * len(adj_list)
        for idx1 in range(len(self.clients)):
            client1 = self.clients[idx1]
            for idx2 in range(idx1 + 1, len(self.clients)):
                client2 = self.clients[idx2]
                if not client1.is_compatible_with(client2):
                    adj_list[idx1].add(idx2)
                    adj_list[idx2].add(idx1)
                    adj_matrix[idx1][idx2] = 1
                    adj_matrix[idx2][idx1] = 1
                    indegree[idx2] += 1
                    indegree[idx1] += 1
        print(f'graph building completed. Total vertex {len(adj_list)}')
        return adj_list, indegree

    def get_max_compatible_clients(self):
        result = self.incompatible_graph.find_max_compatible_vertex_v2()
        return result

    def mark_cliques(self, cliques_visited, groups, client, visited, cliques):
        for item in groups[client]:
            cliques_visited[item] = True
            for c in cliques[item]:
                visited[c] += 1

    def unmark_cliques(self, cliques_visited, groups, client, visited: Set[int], cliques):
        for item in groups[client]:
            cliques_visited[item] = False
            for c in cliques[item]:
                visited[c] = 0 if visited[c] == 1 else visited[c] - 1

    def create_client_clique_groups(self, cliques):
        result = defaultdict(list)
        for idx, clique in enumerate(cliques):
            for client in clique:
                result[client].append(idx)
        return result

    def get_max_compatible_clients_ingredients(self, clients):
        result = set()
        for client in clients:
            client = self.clients[client]
            result.update(client.likes)
            result.difference_update(client.dislikes)
        return result

    def parser(self, file_name):
        data = []
        with open(file_name, 'r') as file:
            line = file.readline()
            while line:
                data.append(line.strip().split())
                line = file.readline()
        return data

    def __str__(self):
        return f'total clients - {len(self.clients)}'


OnePizza(f'data/a_an_example.in.txt').final_result()
OnePizza(f'data/b_basic.in.txt').final_result()
OnePizza(f'data/c_coarse.in.txt').final_result()
OnePizza(f'data/d_difficult.in.txt').final_result()
OnePizza(f'data/e_elaborate.in.txt').final_result()
