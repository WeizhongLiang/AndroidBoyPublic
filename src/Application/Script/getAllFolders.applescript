set _dictFolders to {}
set _filterAccount to ""


log "run with params:"
log "_filterAccount =" & _filterAccount
-- run and output
tell application "Microsoft Outlook"
	if the length of _filterAccount > 0 then
		set _account to the first exchange account whose name is my _filterAccount
	else
		set _account to the first exchange account
	end if
	set _inbox to inbox of _account
	set _folders to every folder of container of _inbox
	
	set _dictSubFolders to {}
	set end of _dictFolders to {_id:_account's name, _name:_account's name, _folders:_dictSubFolders}
	
	set _beginTime to current date
	log "getAllFolders begin at: " & _beginTime
	repeat with _folder in _folders
		my getSubFolder(_folder, _dictSubFolders)
	end repeat
	log "getAllFolders end in: " & (current date) - _beginTime & " seconds"
	
	return my outputJson(my _dictFolders)
end tell


-- output to json format
on outputJson(_dict)
	tell application "JSON Helper"
		set jsonString to make JSON from _dict
		return jsonString
	end tell
end outputJson

on getSubFolder(_curFolder, _dictParent)
	tell application "Microsoft Outlook"
		
		set _dictSubFolders to {}
		set end of _dictParent to {_id:_curFolder's exchange id, _name:_curFolder's name, _folders:_dictSubFolders}
		
		set _folders to every folder of _curFolder
		repeat with _folder in _folders
			my getSubFolder(_folder, _dictSubFolders)
		end repeat
	end tell
end getSubFolder
