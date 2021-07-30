set _dictFilterMails to {}
set _attachmentsFolder to ""
set _filterAccount to ""
set _filterFolder to ""
set _filterStartDate to current date
set _filterEndDate to current date
set _mailsFolder to ""

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
			set my _filterFolder to ln as string
		else if _indexParam = 3 then
			dateObject from ln into my _filterStartDate
		else if _indexParam = 4 then
			dateObject from ln into my _filterEndDate
		else if _indexParam = 5 then
			set my _mailsFolder to ln
		end if
		set _indexParam to _indexParam + 1
	end repeat
	
	-- prepare download folder
	tell application "Microsoft Outlook"
		set _documentFolder to (path to documents folder as string)
		set my _attachmentsFolder to _documentFolder & "Attachments"
		
		tell application "Finder"
			if not (exists my _attachmentsFolder) then
				make new folder at _documentFolder with properties {name:"Attachments"}
			end if
		end tell
		
		if my isFolderExists(my _mailsFolder) then
			log "folder exist: " & my _mailsFolder
		else
			log "folder not exist: " & my _mailsFolder
		end if
	end tell
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

on isFolderExists(_path)
	set _script to "[ -d '" & _path & "' ] && echo true || echo false"
	return (do shell script _script) as boolean
end isFolderExists

on createFolder(_parent, _folderNmae)
	set _newFolder to _parent & "/" & _folderNmae
	set _exist to my isFolderExists(_newFolder)
	if not _exist then
		set _cmd to "mkdir '" & _newFolder & "'"
		do shell script _cmd
	end if
	return _newFolder
end createFolder

my initParams("as_params.cfg")

log "run with params:"
log "_filterAccount =" & _filterAccount
log "_filterFolder =" & _filterFolder
log "_filterStartDate =" & _filterStartDate
log "_filterEndDate =" & _filterEndDate
log "_mailsFolder =" & _mailsFolder

-- run and output
tell application "Microsoft Outlook"
	if the length of _filterAccount > 0 then
		set _account to the first exchange account whose name is my _filterAccount
	else
		set _account to the first exchange account
	end if
	set _inbox to inbox of _account
	set _folders to every folder of container of _inbox
	
	set _beginTime to current date
	log "readFromFolder begin at: " & _beginTime
	repeat with _folder in _folders
		my readFromFolder(_folder)
	end repeat
	log "readFromFolder end in: " & (current date) - _beginTime & " seconds"
	
	return my outputJson(my _dictFilterMails)
end tell

-- output to json format
on outputJson(_dict)
	tell application "JSON Helper"
		set jsonString to make JSON from _dict
		return jsonString
	end tell
end outputJson

on readFromFolder(_curFolder)
	tell application "Microsoft Outlook"
		my filterFolder(_curFolder)
		set _folders to every folder of _curFolder
		repeat with _folder in _folders
			my readFromFolder(_folder)
		end repeat
	end tell
end readFromFolder

on filterFolder(_folder)
	tell application "Microsoft Outlook"
		if _folder's name = my _filterFolder then
			set _folderID to _folder's exchange id
			set _repeatCount to 0
			set _beginTime to current date
			log "generateMailInfo begin at: " & _beginTime
			repeat with _message in messages of _folder
				set _generaResult to my generateMailInfo(_message, my _dictFilterMails, _folderID)
				if _generaResult < 0 then
					exit repeat
				else if _generaResult = 0 then
					set _repeatCount to _repeatCount + 1
				end if
			end repeat
			log "generateMailInfo end for " & _repeatCount & " mails in: " & (current date) - _beginTime & " seconds"
		end if
	end tell
end filterFolder

on generateMailInfo(_message, _dictFolder, _folderID)
	tell application "Microsoft Outlook"
		set _receivedTime to _message's time received
		if _receivedTime < my _filterStartDate then
			return -1
		end if
		if _receivedTime > my _filterEndDate then
			return 1
		end if
		
		set _receivedTimeStr to my dateToString(_receivedTime)
		set _mailID to _message's exchange id
		set _sender to _message's sender
		set _senderName to _sender's name
		set _senderAddress to _sender's address
		
		-- create temp folder for mail
		set _mailTmpFolder to my createFolder(my _mailsFolder, _receivedTimeStr & "_" & _senderAddress)
		
		set _dictMailInfo to {_id:_mailID, _folderID:_folderID, _subject:_message's subject, _senderName:_senderName, _senderEmail:_senderAddress, _receivedTime:_receivedTimeStr, _body:_message's plain text content}
		set _dictAttachments to my appendAttachments(_message, _dictMailInfo, _mailTmpFolder)
		set _dictMailInfo to _dictMailInfo & {_attachments:_dictAttachments}
		set end of _dictFolder to {_mails:_dictMailInfo}
		return 0
	end tell
end generateMailInfo

on appendAttachments(_message, _dictMailInfo, _mailTmpFolder)
	tell application "Microsoft Outlook"
		set _dictAttachment to {}
		set _attachments to attachments of _message
		repeat with _attachment in _attachments
			set _attachmentName to _attachment's name
			set _savedPath to _mailTmpFolder & "/" & _attachmentName
			set _tmpPath to my _attachmentsFolder & ":" & _attachmentName
			try
				if my isFileExists(_savedPath) then
				else
					-- log "download " & _savedPath
					tell application "Finder"
						if (exists _tmpPath) then
						else
							save _attachment in _tmpPath
						end if
						-- Move to correct folder
						move _tmpPath to POSIX file _mailTmpFolder with replacing
					end tell
				end if
				
				set end of _dictAttachment to {_name:_attachmentName, _size:_attachment's file size, _path:_savedPath}
			on error
				log "save " & _tmpPath & " to " & _savedPath & " failed."
			end try
		end repeat
		return _dictAttachment
	end tell
end appendAttachments

-- commond function
on pad(v)
	return text -2 thru -1 of ((v + 100) as text)
end pad

on dateToString(_date)
	set {year:yr, month:mn, day:dy, hours:h, minutes:mi, seconds:s} to (_date)
	set dateString to pad(mn as integer) & pad(dy) & (yr as text) & "_" & pad(h as integer) & pad(mi as integer) & pad(s as integer)
end dateToString

to dateObject from theDateString into myDate
	set {oti, text item delimiters} to {text item delimiters, " "}
	set {dateString, timeString} to text items of theDateString
	set text item delimiters to ":"
	set {hrs, mins, secs} to text items of timeString
	
	-- this line was in error in the original script. The ApplesScript constent for
	-- minutes is minutes not mins!!
	set hrsMins to hrs * hours + mins * minutes + secs
	set {yr, Mnth, dy} to words of dateString
	set the time of myDate to hrsMins
	set the year of myDate to yr
	set the month of myDate to Mnth
	set the day of myDate to dy
	set text item delimiters to oti
end dateObject
