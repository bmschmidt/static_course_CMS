from coursebuilder.build_site_components import files, build_site, path_filter
import sys

if __name__=="__main__":
    try:
        argument = sys.argv[1]
    except IndexError:
        raise NameError("Usage: python scripts/build_site_components.py ARG\n"
              "where ARG is one of 'build', 'markdown', 'pdfs', 'webpdfs'")
    try:
        future = sys.argv[2]
    except:
        future = False
    if argument == 'build':
        build_site()
    elif argument in ['markdown', 'pdf', 'webpdf', 'epub', 'slides']:
        names = [str(f) for f in files(argument) if path_filter(f)]
        print(' '.join(names))
    else:
        print ("No sensible args")
