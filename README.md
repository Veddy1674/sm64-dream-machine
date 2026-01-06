## Note: I consider this project *old* and not quite useful for anything, I could say it was an experiment of the old me, not something long-term. This project, or atleast, this branch, will be left as it is. Just as a memory for myself, as I made this when I was roughly 15 to 16 years old, I believe. Cheers everyone!
Also, I see that I couldn't really understand the complexity of this all, and I believe some of the scripts were COMPLETELY AI generated, so well... If any good soul wishes to continue this project, peraphs in a simpler environment than "the whole super mario 64 game", go ahead!

# Super Mario 64 - Dream Machine
Inspired by Oasis and DeepMind's "dream" machines.

This 'inputbased' branch is another (and slightly better) experiment, where from a single frame you can press a key and the AI will predict the image, all this in real-time (30+ fps), there are many issues, but if you're curious how it looks like, my best attempt is saved in the folder `success`: bring the *inputs.txt* inside *videos/*, the *dreamnet.pth* in the project root and extract *frames.zip* inside *frames/*, then run **realtime_predict.py** (preferably in VSCode), from there you can predict the next frame using WASD to move (no A, B, Z or other buttons), R to reset (sets to 'frame_00000.png'), ESC to end.



Normally, to train the "dreamnet" with your own frames, you have to:

   **1.** In your Mupen64 emulator, **run `avicapture.lua`** or the variants and do what the script says.
   
   **2.** This will save one or more videos to `videos/`, so **run `aviToPng.py`** to convert the videos into 96x96 borderless .png images (inside `preframes/`).
   
   **3.** **Run `checksum.lua`** to remove duplicated frames, because Mupen64 records at 60 fps, the 1st and 3rd frame are identical, same with 3rd and 5th, 5th and 7th and so on.
   
   **4.** **Train your dreamnet with `train_model.py`**, I personally used *Google Colab* for this.
   
   **5.** After the training you will end up with a `dreamnet.pth` in your project root, **run `realtime_predict.py`** and see the results.



After all of this, you can delete your *heavy* videos in `videos/` and the images in `preframes/`, it will still work.

Why *heavy*? Well, I must mention your Mupen64's capture settings must be set to raw frames, no compression, meaning a 23 second video will weigh about 2 GB.

Optional: set the capture sync setting to "None", by default it's "Audio", which slows down the recording slightly.
