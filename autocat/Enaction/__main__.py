from pyrr import line
from .Predict import x_intersection, y_intersection

# Test prediction
# py -m autocat.Enaction


print("=== Test x segment intersection ===")
l1 = line.create_from_points([1, -1], [2, 1])
print("Intersection", str(x_intersection(l1)))
l2 = line.create_from_points([1, 1], [2, -1])
print("Intersection", str(x_intersection(l2)))
l3 = line.create_from_points([1, -1], [1, 1])
print("Intersection", str(x_intersection(l3)))
l4 = line.create_from_points([1, -1], [2, 20])
print("Intersection", str(x_intersection(l4)))
l5 = line.create_from_points([1, -1], [2, -2])
print("Intersection", str(x_intersection(l5)))

print("=== Test Y segment intersection ===")
l6 = line.create_from_points([-1, 1], [1, 2])
print("Intersection", str(y_intersection(l6)))
l7 = line.create_from_points([-1, -1], [1, -1])
print("Intersection", str(y_intersection(l7)))
l8 = line.create_from_points([-1, -1], [-1, 1])
print("Intersection", str(y_intersection(l8)))
