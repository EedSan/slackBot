import logging

from app import main

if __name__ == "__main__":
    logging.basicConfig(filename='developing_log.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    main()
