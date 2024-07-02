
@app.route('/update_video_status/<int:video_id>', methods=['POST'])
def update_video_status(video_id):
    if 'loggedin' not in session or session.get('user_type') != 0:
        return redirect(url_for('login'))

    new_status = request.form.get('status')
    author = {
        "user_id": session.get("user_id"),
        "user_email": session.get("user_email"),
        "user_type": session.get("user_type"),
    }

    try:
        vidschool.set_video_status(video_id, new_status, author)
        msg = 'Channel status updated successfully!'
    except Exception as e:
        msg = f'Error: {str(e)}'

    return redirect(url_for('view_videos', msg=msg))