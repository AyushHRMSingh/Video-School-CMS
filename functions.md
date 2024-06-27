# Main Functions:-
<!-- referring to extfun.py file functions -->

- `hash_password(password: str) -> str`: This funcitons takes a password as input and returns the hashed and salted version of the password

- `setupdb()`: This function connects to MySQL and creates the main VIDEOSCHOOL database and the required tables with the defined schema

- `add_user(email:str, password:str, role:int, author:dict)`: This function adds a new user to the database

- `delete_user(id:int, author:dict)`: This function sets the status of the user to 1

- `get_user(id:int)`: This function returns the user details of the given user id

- `add_video(video_name:str, creator_id:int, editor_id:int, manager_id:int, author:dict)`: This function adds a new video to the database

- `update_video(video_id:int, video_name:str, creator_id:int, editor_id:int, manager_id:int, author:dict)`: This function updates the video details

- `set_video_status(video_id:int, status:int, author:dict, message:string (optional)`: This function sets the status of the video to the defined value

- `set_delete_video(video_id:int, author:dict)`: This function sets the status of the video to 7

- `get_videos()`: This function returns the list of videos

- `get_video(video_id:int)`: This function returns the details of the video

- `add_channel(channel_id:int, channel_name:str, platform:str, author:dict)`: This function adds a new channel to the database

- `delete_channel(channel_id:int, author:dict)`: This function sets the status of the channel to 3

- `edit_channel(channel_id:int, channel_name:str, platform:str, author:dict)`: This function updates the channel details to those that are set

- `update_channel_status(channel_id:int, status:int, author:dict)`: This function sets the status of the channel to the defined value

- `get_channels()`: This function returns the list of channels

- `get_channel(channel_id:int)`: This function returns the details of the channel

- `assign_user_to_channel(user_id:int, channel_id:int, user_type:int, author:dict)`: This function assigns a user to a channel with the defined role