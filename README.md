# distributed-cipher
A Python 3/4 distributed cipher encoder and decoder

Version 1.0

This script encodes a specified file into four separate encoded files with the command: dist_cipher.py -e <filename>
A copy of the original specified file may be obtained if any three, but no less, of the four encoded files are available by using
the command: dist_cipher.py -d <filename>
  
The way the encoding works is to represent each bit of the original file in the encoded files with two bits. The two bits
may be a number from 0 to 3.

A 0 is encoded by choosing one set from the following sets:
0, 0, 1, 1;
1, 1, 2, 2;
2, 2, 3, 3;
0, 0, 2, 2;
1, 1, 3, 3;
0, 0, 3, 3;
And then randomly assigning each of the numbers of the chosen set to be the 'two bits' for one of the encoded cipher files.

Likewise, a 1 is encoded by choosing one set from the following sets:
0, 1, 2, 3;
0, 0, 0, 0;
1, 1, 1, 1;
2, 2, 2, 2;
3, 3, 3, 3;
And then randomly assigning each of the numbers of the chosen set to be the 'two bits' for one of the encoded cipher files.

If we randomly picked two numbers from any one set of the '0' sets, there is a 1/3 probability that they would be the same,
and a 2/3 probability that they would be different. If we make the chance of choosing the 0, 1, 2, 3 set equal to 2/3 when
we need to choose a '1' set, then there is no way to determine whether an original bit was a 0 or a 1 if you only have two
numbers from your selected set. Three numbers from the selected set are needed to determine what the original bit was.

Only three of the four encoded files are needed to recover a copy of the original file. This allows for recovery of the original
file even if one of the encoded files is unavailable.
