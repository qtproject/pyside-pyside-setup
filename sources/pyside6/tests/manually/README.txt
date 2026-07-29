To run these tests, some manual input is necessary (most of them not supported by QTest[1]),
because of that this is not part of automatic test context.

freethreading/ is here for a different reason: it proves that the object graph
guard is needed by running the same stress twice, once with the guard disabled,
where the point is that the processes die. See freethreading/run.py.


[1]https://qt-project.atlassian.net/browse/QTBUG-13397
