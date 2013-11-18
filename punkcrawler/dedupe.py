import sys

def dedupe(infilename):

    lines_seen = set() # holds lines already seen
    for line in open(infilename, "r"):
        if line not in lines_seen: # not a duplicate
            print line
            lines_seen.add(line)
    
if __name__ == "__main__":
    
    dedupe(sys.argv[1])