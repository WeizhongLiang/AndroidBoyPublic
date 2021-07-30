set _dictFolders to {}
set _filterAccount to ""
set _filterRecipient to ""

on initParams(_fileName)
	set srcFile to ((path to desktop) as text) & _fileName
	if not my isFileExistsMac(srcFile) then
		log "file: " & srcFile & " not exist, use default parameters."
		return
	end if
	
	set lns to paragraphs of (read file srcFile)
	set _indexParam to 1
	repeat with ln in lns
		if _indexParam = 1 then
			set my _filterAccount to ln as string
		else if _indexParam = 2 then
			set my _filterRecipient to ln as string
		end if
		set _indexParam to _indexParam + 1
	end repeat
end initParams

on isFileExistsMac(_path) -- (String) as Boolean
	tell application "System Events"
		if exists file _path then
			return true
		else
			return false
		end if
	end tell
end isFileExistsMac

on isFileExists(_path)
	set _script to "[ -f '" & _path & "' ] && echo true || echo false"
	return (do shell script _script) as boolean
end isFileExists

my initParams("as_params.cfg")

log "run with params:"
log "_filterAccount =" & _filterAccount
log "_filterRecipient =" & _filterRecipient

-- run and output
tell application "Microsoft Outlook"
	if the length of _filterAccount > 0 then
		set _account to the first exchange account whose name is my _filterAccount
	else
		set _account to the first exchange account
	end if
	set _inbox to inbox of _account
	set _folders to every mail folder of container of _inbox
	
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
		set _findRecipent to false
		if (count of my _filterRecipient) > 0 then
			if (count of message of _curFolder) > 0 then
				set _message to the first message of _curFolder
				set _recipients to _message's to recipients
				repeat with _recipient in _recipients
					set _recipientMail to (_recipient's email address)
					set _recipientAddress to _recipientMail's address
					if _recipientAddress = my _filterRecipient then
						set _findRecipent to true
						exit repeat
					end if
				end repeat
			end if
		end if
		
		set _dictSubFolders to {}
		set end of _dictParent to {_id:_curFolder's exchange id, _name:_curFolder's name, _containRecipent:_findRecipent, _folders:_dictSubFolders}
		
		set _folders to every mail folder of _curFolder
		repeat with _folder in _folders
			my getSubFolder(_folder, _dictSubFolders)
		end repeat
	end tell
end getSubFolder
