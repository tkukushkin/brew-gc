import subprocess
from heapq import heapify, heappop, heappush


def main() -> None:
    print('Fetching installed packages and it\'s dependencies... ', end='')
    proc = subprocess.run(['brew', 'list', '--full-name', '--quiet'], capture_output=True, check=True)
    packages = proc.stdout.decode('utf-8').split()

    dependencies: dict[str, set[str]] = {name: set() for name in packages}
    parents: dict[str, set[str]] = {name: set() for name in packages}

    proc = subprocess.run(['brew', 'deps', '--for-each', *packages], capture_output=True, check=True)
    for line in proc.stdout.decode('utf-8').strip().split('\n'):
        name, deps_str = line.split(':')
        deps = deps_str.split()
        dependencies[name].update(deps)
        for dep in deps:
            parents[dep].add(name)

    print('done')

    queue = [name for name, pars in parents.items() if not pars]
    heapify(queue)

    while queue:
        name = heappop(queue)

        if input(f'Would you like to uninstall {name}? [y/N]: ').lower() != 'y':
            continue

        subprocess.run(['brew', 'uninstall', '--force', name], check=True)

        for pkg in dependencies[name]:
            parents[pkg].remove(name)
            if not parents[pkg]:
                heappush(queue, pkg)

        del parents[name]
        del dependencies[name]


if __name__ == '__main__':
    main()
