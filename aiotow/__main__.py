

def run(args):
    """Run
    """
    print(args)


if __name__ == '__main__':
    from aiotow import __version__
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()
    run(args)
