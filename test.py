from extfun import VidSchool
import envfile
from sqlsetup import mainB

host = envfile.host
username = envfile.dbuser
password = envfile.dbpass
dbname = envfile.dbname

def Main():
    print('Test')
    mainB()
    obj = VidSchool(host, username, password, dbname)
    obj.setupdb()
    testuser(obj)
    testvideo(obj)
    testchannel(obj)
    logs = obj.get_logs()
    for log in logs:
        print(log)

def printarr(arr):
    print('Printing array')
    for i in arr:
        print(i)

typea = 2

### CHECKED WORKING AS OF 
def testuser(obj:VidSchool):
    printarr(obj.get_users({'user_type':typea,'user_id':1}))
    # add user
    obj.add_user('ayush@mail.com', 'pass', 1, {'user_type':typea,'user_id':1})
    printarr(obj.get_users({'user_type':typea,'user_id':1}))
    obj.add_user('prasad@mail.com', 'pass', 1, {'user_type':typea,'user_id':1})
    printarr(obj.get_users({'user_type':typea,'user_id':1}))
    print('single')
    print(obj.get_user(1))
    print(obj.get_user(2))
    # edit user
    obj.edit_user(2, 'ayush2@mail.com', 'pass2', 0, {'user_type':typea,'user_id':1})
    printarr(obj.get_users({'user_type':typea,'user_id':1}))
    # user login
    print("login")
    print(obj.login_user('ayush2@mail.com', 'pass2'))
    print(obj.login_user('ayush@main.com', 'pass'))
    # user delete
    obj.delete_user(2, {'user_type':typea,'user_id':1})
    printarr(obj.get_users({'user_type':typea,'user_id':1}))

def testvideo(obj:VidSchool):
    printarr(obj.get_videos({'user_type':typea,'user_id':1}))
    # add videos
    obj.add_video(1, 'video1', 1,2,3,4,{'user_type':typea,'user_id':1})
    printarr(obj.get_videos({'user_type':typea,'user_id':1}))
    obj.add_video(1, 'video2', 1,2,3,5,{'user_type':typea,'user_id':1})
    printarr(obj.get_videos({'user_type':typea,'user_id':1}))
    # set status
    obj.set_video_status(1,2,{'user_type':typea,'user_id':1}, "AN UPDATE?????")
    obj.get_video(1)
    obj.get_video(2)
    # update video deets
    obj.update_video(1, 'video3', 4,3,2,1,{'user_type':typea,'user_id':1})
    printarr(obj.get_videos({'user_type':typea,'user_id':1}))
    obj.set_delete_video(2, {'user_type':typea,'user_id':1})
    printarr(obj.get_videos({'user_type':typea,'user_id':1}))

def testchannel(obj:VidSchool):
    printarr(obj.get_channels())
    obj.add_channel('channel1', 'https:url.com',1, {'user_type':typea,'user_id':1})
    printarr(obj.get_channels())
    obj.add_channel('channel2', 'https:url.com',1, {'user_type':typea,'user_id':1})
    printarr(obj.get_channels())
    obj.get_channel(1)
    obj.get_channel(2)
    obj.edit_channel(1, 'channel3', 'https:url.com',1, {'user_type':typea,'user_id':1})
    printarr(obj.get_channels())
    obj.update_channel_status(1, 3, {'user_type':typea,'user_id':1})
    obj.delete_channel(2, {'user_type':typea,'user_id':1})
    printarr(obj.get_channels())


if __name__ == '__main__':
    Main()