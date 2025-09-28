# Claude instructions for fidchar

## Technology and Framework Requirements
    * You shall write code in Python
    * You shall use Python latest and standard package management (uv preferred) for non ROS2 programs
    * You shall use ROS2 and colcon builds for ROS2 programs
    * You should prefer async/await over threading when there is a choice
    * You should look for existing libraries instead of reinventing solutions

## Code Structure and Organization
    * You shall ensure functions and methods are no longer than 50 lines
    * You shall ensure no files have more than about 300 lines
    * You shall use classes and put them in separate files
    * You shall put data classes in the file where they are constructed
    * You shall name files after the class defined in the file
    * You shall give methods intention-revealing names
    * You shall avoid if/else statements that are nested more than 1 deep. If tempted to do so, look for another design
    * You shall not have if statements with more than 3 branches. If tempted to do so, look for another design
    * You shall avoid 2 line methods
    * You shall avoid 1 line functions and methods
    * You shall avoid simple wrappers
    * You should look for code duplication and make the code DRY if it makes sense

## Code Quality and Best Practices
    * You shall write idiomatic Python
    * You should not go overboard on error checking
    * You shall never have bare except Exception: you shall be specific, and also put something in the alert box
    * You shall not assign the result of a function to a variable just to use that variable one time only; you shall use the function call directly
    * You shall put a comment with each method or function ONLY if the name of the function is not sufficient by itself
    * You should almost always use double quotes; you shall only use single quotes if there is a specific requirement to do so
    * You shall undertake multi-step implementation or refactoring in a way that after each step a running program is retained so that testing can be done to ensure progress is on the right track
    * You shall not provide default parameters to functions; make the caller provide all required values explicitly
    * You shall not code defensively; let exceptions bubble up rather than handling every possible error case
    
    
# CURRENT.md
    * Now read CURRENT.md and follow it's instructions
