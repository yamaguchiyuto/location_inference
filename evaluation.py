import lib.util as util

class Evaluation:
    def __init__(self, test_users):
        self.test_users = test_users

    def average_error_distance(self, inferred_users):
        error_sum = .0
        inferred_count = 0
        for test_user in self.test_users.iter():
            true_point = test_user['location_point']
            inferred_point = inferred_users.get(test_user['id'])['location_point']
            if not inferred_point == None:
                error_sum += util.hubeny_distance(inferred_point, true_point)
                inferred_count += 1
        return error_sum / inferred_count

if __name__ == '__main__':
    import sys
    from lib.users import Users
    from lib.graph import Graph
    from naiveg.naiveg import NaiveG

    if len(sys.argv) < 4:
        print '[usage]: python %s [test users file path] [training users file path] [graph file path]' % sys.argv[0]
        exit()

    test_users = Users()
    test_users.load_file(sys.argv[1])
    ev = Evaluation(test_users)

    training_users = Users()
    training_users.load_file(sys.argv[2])
    graph = Graph()
    graph.load_file(sys.argv[3])
    method = NaiveG(training_users, graph)
    method.infer()

    inferred_users = method.get_users()
    print ev.average_error_distance(inferred_users)
