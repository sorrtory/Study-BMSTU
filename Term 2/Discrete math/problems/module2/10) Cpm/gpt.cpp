#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <stack>
#include <algorithm>

struct Task {
    std::string name;
    int duration;
    std::vector<std::string> dependencies;
};

std::unordered_map<std::string, Task> parseInput() {
    std::unordered_map<std::string, Task> tasks;
    std::unordered_map<std::string, bool> seen;
    std::string input;
    std::getline(std::cin, input);
    std::stringstream ss(input);
    std::string segment;
    
    while (std::getline(ss, segment, ';')) {
        std::stringstream ssegment(segment);
        std::string item;
        std::string lastTask;
        while (std::getline(ssegment, item, '<')) {
            item.erase(0, item.find_first_not_of(" \t\n\r\f\v"));
            item.erase(item.find_last_not_of(" \t\n\r\f\v") + 1);
            size_t pos = item.find('(');
            std::string taskName = (pos != std::string::npos) ? item.substr(0, pos) : item;
            int duration = (pos != std::string::npos) ? std::stoi(item.substr(pos + 1, item.find(')') - pos - 1)) : 0;
            
            if (tasks.find(taskName) == tasks.end()) {
                tasks[taskName] = {taskName, duration, {}};
            }
            
            if (!lastTask.empty()) {
                tasks[lastTask].dependencies.push_back(taskName);
            }
            
            lastTask = taskName;
        }
    }
    
    return tasks;
}

bool detectCycleUtil(const std::string& task, const std::unordered_map<std::string, Task>& tasks, std::unordered_set<std::string>& visited, std::unordered_set<std::string>& recStack) {
    if (recStack.find(task) != recStack.end()) {
        return true;
    }
    
    if (visited.find(task) != visited.end()) {
        return false;
    }
    
    visited.insert(task);
    recStack.insert(task);
    
    for (const auto& dep : tasks.at(task).dependencies) {
        if (detectCycleUtil(dep, tasks, visited, recStack)) {
            return true;
        }
    }
    
    recStack.erase(task);
    return false;
}

bool detectCycle(const std::unordered_map<std::string, Task>& tasks, std::unordered_set<std::string>& cyclicTasks) {
    std::unordered_set<std::string> visited;
    std::unordered_set<std::string> recStack;
    
    for (const auto& taskPair : tasks) {
        if (detectCycleUtil(taskPair.first, tasks, visited, recStack)) {
            cyclicTasks.insert(taskPair.first);
        }
    }
    
    return !cyclicTasks.empty();
}

std::vector<std::string> topologicalSort(const std::unordered_map<std::string, Task>& tasks, const std::unordered_set<std::string>& cyclicTasks) {
    std::unordered_map<std::string, int> inDegree;
    std::queue<std::string> zeroInDegreeQueue;
    std::vector<std::string> sortedTasks;
    
    for (const auto& taskPair : tasks) {
        inDegree[taskPair.first] = 0;
    }
    
    for (const auto& taskPair : tasks) {
        if (cyclicTasks.find(taskPair.first) == cyclicTasks.end()) {
            for (const auto& dep : taskPair.second.dependencies) {
                if (cyclicTasks.find(dep) == cyclicTasks.end()) {
                    inDegree[dep]++;
                }
            }
        }
    }
    
    for (const auto& taskPair : tasks) {
        if (inDegree[taskPair.first] == 0 && cyclicTasks.find(taskPair.first) == cyclicTasks.end()) {
            zeroInDegreeQueue.push(taskPair.first);
        }
    }
    
    while (!zeroInDegreeQueue.empty()) {
        std::string task = zeroInDegreeQueue.front();
        zeroInDegreeQueue.pop();
        sortedTasks.push_back(task);
        
        for (const auto& dep : tasks.at(task).dependencies) {
            if (--inDegree[dep] == 0) {
                zeroInDegreeQueue.push(dep);
            }
        }
    }
    
    return sortedTasks;
}

std::vector<std::string> findCriticalPath(const std::unordered_map<std::string, Task>& tasks, const std::vector<std::string>& topSortedTasks) {
    std::unordered_map<std::string, int> dist;
    std::unordered_map<std::string, std::string> pred;
    
    for (const auto& task : topSortedTasks) {
        dist[task] = (task == topSortedTasks.front()) ? tasks.at(task).duration : 0;
    }
    
    for (const auto& task : topSortedTasks) {
        for (const auto& dep : tasks.at(task).dependencies) {
            if (dist[dep] < dist[task] + tasks.at(dep).duration) {
                dist[dep] = dist[task] + tasks.at(dep).duration;
                pred[dep] = task;
            }
        }
    }
    
    std::vector<std::string> criticalPath;
    std::string maxDistTask = topSortedTasks.front();
    for (const auto& task : topSortedTasks) {
        if (dist[task] > dist[maxDistTask]) {
            maxDistTask = task;
        }
    }
    
    for (std::string at = maxDistTask; !at.empty(); at = pred[at]) {
        criticalPath.push_back(at);
    }
    
    std::reverse(criticalPath.begin(), criticalPath.end());
    return criticalPath;
}

void printDotFormat(const std::unordered_map<std::string, Task>& tasks, const std::unordered_set<std::string>& cyclicTasks, const std::vector<std::string>& criticalPath) {
    std::cout << "digraph G {" << std::endl;
    
    std::unordered_set<std::string> criticalPathSet(criticalPath.begin(), criticalPath.end());
    
    for (const auto& taskPair : tasks) {
        if (cyclicTasks.find(taskPair.first) != cyclicTasks.end()) {
            std::cout << "  \"" << taskPair.first << "\" [label=\"" << taskPair.first << "(" << taskPair.second.duration << ")\", color=blue];" << std::endl;
        } else if (criticalPathSet.find(taskPair.first) != criticalPathSet.end()) {
            std::cout << "  \"" << taskPair.first << "\" [label=\"" << taskPair.first << "(" << taskPair.second.duration << ")\", color=red];" << std::endl;
        } else {
            std::cout << "  \"" << taskPair.first << "\" [label=\"" << taskPair.first << "(" << taskPair.second.duration << ")\"];" << std::endl;
        }
    }
    
    for (const auto& taskPair : tasks) {
        for (const auto& dep : taskPair.second.dependencies) {
            if (cyclicTasks.find(taskPair.first) != cyclicTasks.end() || cyclicTasks.find(dep) != cyclicTasks.end()) {
                std::cout << "  \"" << taskPair.first << "\" -> \"" << dep << "\" [color=blue];" << std::endl;
            } else if (criticalPathSet.find(taskPair.first) != criticalPathSet.end() && criticalPathSet.find(dep) != criticalPathSet.end()) {
                std::cout << "  \"" << taskPair.first << "\" -> \"" << dep << "\" [color=red];" << std::endl;
            } else {
                std::cout << "  \"" << taskPair.first << "\" -> \"" << dep << "\";" << std::endl;
            }
        }
    }
    
    std::cout << "}" << std::endl;
}

int main() {
    auto tasks = parseInput();
    
    std::unordered_set<std::string> cyclicTasks;
    if (detectCycle(tasks, cyclicTasks)) {
        std::cerr << "Cyclic dependencies detected!" << std::endl;
    }
    
    auto topSortedTasks = topologicalSort(tasks, cyclicTasks);
    auto criticalPath = findCriticalPath(tasks, topSortedTasks);
    
    printDotFormat(tasks, cyclicTasks, criticalPath);
    
    return 0;
}
