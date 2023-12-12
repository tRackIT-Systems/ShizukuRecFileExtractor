from shizuku import ShizukuRec

with open("etc/example.ShizukuRec", "rb") as fd:
    rec = ShizukuRec(fd)

print(f"Duration: {rec.duration} s")

print(f"Average voltage: {sum(rec.voltage) / rec.samples:.3f} V")
print(f"Average current: {sum(rec.current) / rec.samples:.3f} A")

print(f"Total energy: {sum(rec.energy):.3f} Wh")
print(f"Total capacity: {sum(rec.capacity):.3f} Ah")
