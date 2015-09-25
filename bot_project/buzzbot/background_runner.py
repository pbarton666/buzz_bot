from threading import Thread

class BackgroundRunner(Thread):
    """
    Runs methods in background.

    Example code:
        # Load library
        from background_runner import BackgroundRunner

        # Method to call in background
        def adder(x, y):
            return x + y

        # Method to notify when background task is completed
        def notify(runner):
            print "Result: %s" % runner.result

        # Create runner and run task
        runner = BackgroundRunner(method=adder, notify=notify, params={"x": 41, "y": 1})
        runner.start()

        # When run, the above code will produce output similar to:
        BackgroundRunner#147858316: starting
        Result: 42
        BackgroundRunner#147858316: finished
    """

    def __init__(self, method, notify=None, message=None, params={}):
        """
        Instantiates a background runner.

        Keyword arguments:
        * method: A method to run in the background.
        * params: Parameters dict to pass to method as kwargs.
        * notify: A method to call when finished, passing a reference to this runner object.
        * message: Message to include when reporting status.
        """
        Thread.__init__(self)
        self.result = None

        self.method = method
        self.notify = notify
        self.message = message or ""
        self.params = params
        self.finished = False

    def start(self):
        """
        Runs this background task. Because this method will run in the
        background, it provides no meaningful return value. However,
        you can monitor the task by checking the following instance
        variables:

        * `finished`: Is the task finished? Boolean.
        * `result`: Result of the task when finished. Object.
        """
        return super(BackgroundRunner, self).start()

    def run(self):
        """
        DO NOT CALL THIS METHOD YOURSELF! Use `start` instead!
        """
        print "BackgroundRunner#%s: starting %s" % (id(self), self.message)
        try:
            self.result = self.method(**self.params)
        except Exception, e:
            self.result = e
        self.finished = True
        if self.notify:
            self.notify(self)
        print "BackgroundRunner#%s: finished %s" % (id(self), self.message)

