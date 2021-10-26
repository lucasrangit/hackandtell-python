#include <iostream>

#include <SDL/SDL.h>

int main(int argc, char * argv[])
{
	// Initialize SDL with video
	SDL_Init(SDL_INIT_VIDEO);
	
	// Create a window with SDL
	if(SDL_SetVideoMode(640, 480, 32, SDL_DOUBLEBUF | SDL_OPENGL) == 0)
	{
		std::cerr << "Failed to set video mode\n";
		return 1;
	}
	
	
	SDL_Event event;	 // used to store any events from the OS
	bool running = true; // used to determine if we're running the game
	
	while(running)
	{
		// poll for events from SDL
		while(SDL_PollEvent(&event))
		{
			// determine if the user still wants to have the window open
			// (this basically checks if the user has pressed 'X')
			running = event.type != SDL_QUIT;
		}
		
		// Swap OpenGL buffers
		SDL_GL_SwapBuffers();
	}
	
	// Quit SDL
	SDL_Quit();
	
    return 0;
}