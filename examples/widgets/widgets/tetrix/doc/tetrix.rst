Tetrix
======

The Tetrix example is a Qt version of the classic Tetrix game.

.. image:: tetrix-screenshot.png
  :width: 400
  :alt: Tetrix main window

The object of the game is to stack pieces dropped from the top of the playing
area so that they fill entire rows at the bottom of the playing area.

When a row is filled, all the blocks on that row are removed, the player earns
a number of points, and the pieces above are moved down to occupy that row. If
more than one row is filled, the blocks on each row are removed, and the player
earns extra points.

The **Left** cursor key moves the current piece one space to the left, the
**Right** cursor key moves it one space to the right, the **Up** cursor key
rotates the piece counter-clockwise by 90 degrees, and the **Down** cursor key
rotates the piece clockwise by 90 degrees.

To avoid waiting for a piece to fall to the bottom of the board, press **D** to
immediately move the piece down by one row, or press the **Space** key to drop
it as close to the bottom of the board as possible.

This example shows how a simple game can be created using only three classes:

* The ``TetrixWindow`` class is used to display the player's score, number of
  lives, and information about the next piece to appear.
* The ``TetrixBoard`` class contains the game logic, handles keyboard input, and
  displays the pieces on the playing area.
* The ``TetrixPiece`` class contains information about each piece.

In this approach, the ``TetrixBoard`` class is the most complex class, since it
handles the game logic and rendering. One benefit of this is that the
``TetrixWindow`` and ``TetrixPiece`` classes are very simple and contain only a
minimum of code.
