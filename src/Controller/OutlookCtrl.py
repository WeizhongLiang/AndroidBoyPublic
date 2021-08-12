import copy
import json
import os
from datetime import datetime
from typing import Tuple
from src.Common import SystemHelper, DateTimeHelper, FileUtility
from src.Common.Logger import Logger
from src.Model.AppModel import appModel


class EmailFilter:
    def __init__(self, folderArray=None, toArray=None, senderArray=None, receiverArray=None):
        self.folders = folderArray  # [str]
        self.tos = toArray  # [str]
        self.senders = senderArray  # [str]
        self.receivers = receiverArray  # [str]
        self.beginDate = 0
        self.endDate = 0
        return


class AccountObjectMac:
    def __init__(self, name):
        self.UserName = name
        self.DisplayName = name
        self.AccountType = 0
        return


class AccountItem:
    def __init__(self, accountObject, outlook):
        self.mAccountObject = accountObject
        self.mOutlook = outlook
        self.mID = accountObject.UserName
        self.mName = accountObject.DisplayName
        self.mType = accountObject.AccountType
        self.mFolders: [FolderItem] = []
        self.mCustomerData = None
        return


class FolderObjectMac:
    def __init__(self, entryID, name):
        self.EntryID = entryID
        self.Name = name
        return


class FolderItem:
    def __init__(self, folderObject, account: AccountItem):
        self.mFolderObject = folderObject
        self.mAccount: AccountItem = account
        account.mFolders.append(self)
        self.mID = folderObject.EntryID
        self.mName = folderObject.Name
        self.mItems: [EmailItem] = []
        self.mCustomerData = None
        return


class EmailObjectMac:
    def __init__(self, email):
        self.EntryID = email["_id"]
        self.Subject = email["_subject"]
        self.Body = email["_body"]
        self.ReceivedTime = self.getReceivedTime(email["_receivedTime"])
        self.SenderName = email["_senderName"]
        self.SenderEmailAddress = email["_senderEmail"]
        self.ReceivedByName = "receivedByName"
        self.To = "to"
        self.Attachments = []
        return

    @staticmethod
    def getReceivedTime(timeStr) -> datetime:
        return datetime.strptime(timeStr, '%m%d%Y_%H%M%S')


class EmailItem:
    def __init__(self, emailObject, folderItem: FolderItem, localFolderBase: str):
        self.mEmailObject = emailObject
        self.mFolder: FolderItem = folderItem
        folderItem.mItems.append(self)
        self.mID: str = emailObject.EntryID
        self.mSubject: str = emailObject.Subject
        self.mBody: str = emailObject.Body
        self.mReceivedTime: datetime = emailObject.ReceivedTime
        self.mSenderName: str = emailObject.SenderName
        self.mSenderEmail: str = emailObject.SenderEmailAddress
        self.mReceiveName: str = emailObject.ReceivedByName
        self.mToName: str = emailObject.To
        self.mCustomerData = None
        self.mAnalyzer = None  # MailAnalyzer

        # local folder
        # for c in "/\\:*\"<>|?. ":
        #    senderName = self.mSenderName.replace(c, "_")
        localFolder = self.mReceivedTime.strftime("%m%d%Y_%H%M%S_")
        localFolder += self.mSenderEmail
        self.mLocalFolder = os.path.join(localFolderBase, localFolder)
        FileUtility.makeFolder(self.mLocalFolder)

        self.mAttachments = self._saveAttachments(emailObject)
        return

    def _saveAttachments(self, emailObject) -> [str]:
        # Attachments
        attachmentList = []
        attachments = emailObject.Attachments
        for attachment in attachments:
            tmpPath = os.path.join(self.mLocalFolder, f"{attachment.FileName}")
            try:
                if not os.path.exists(tmpPath):
                    attachment.SaveAsFile(tmpPath)
                attachmentList.append(tmpPath)
            except Exception as e:
                Logger.e(appModel.getAppTag(), f"save to = {tmpPath} failed: {e}")
                return attachmentList
        return attachmentList


class OutlookCtrl:
    sLocalFolderBase = ""

    def __init__(self, onReadItem):
        # def onReadItem(email: EmailItem, folder: FolderItem, account: AccountItem, index: int, count: int) -> bool:
        Logger.i(appModel.getAppTag(), "")

        self._mOnReadItem = onReadItem
        self._mAccounts: {str, AccountItem} = {}
        self._mFolders: {str, FolderItem} = {}
        self._mFilterMails: {str, EmailItem} = {}
        return

    # for filter
    def _readFilterEmails(self, folder, emailFilter: EmailFilter) -> int:
        readCount = 0
        folderItem = self._mFolders.get(folder.EntryID)
        if folderItem is None:
            return 0
        folderItem.mItems.clear()
        totalCount = len(folder.Items)
        curIndex = 0
        for email in folder.Items:
            # object class type:
            # https://docs.microsoft.com/en-us/office/vba/api/outlook.olobjectclass
            # object properties:
            # https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.subject
            # don't want to "access warning"? set it in Outlook:
            # "File" -> "Options" -> "Trust Center" -> "Trust Center Settings" -> "Programmatic Access"
            curIndex += 1
            if email.Class != 43:
                continue
            if (emailFilter.tos and email.To in emailFilter.tos) \
                    or (emailFilter.senders and email.Sender in emailFilter.senders) \
                    or (emailFilter.receivers and email.ReceivedByName in emailFilter.receivers):
                # Logger.i(appModel.getAppTag(), f"add mail: to={email.To}, "
                #                                f"sender={email.Sender}, "
                #                                f"receiver={email.ReceivedByName}")
                receivedTime = email.ReceivedTime.timestamp()
                if emailFilter.beginDate != 0 and receivedTime < emailFilter.beginDate:
                    continue
                if emailFilter.endDate != 0 and receivedTime > emailFilter.endDate:
                    continue

                emailItem = EmailItem(email, folderItem, self.sLocalFolderBase)
                self._mFilterMails[emailItem.mID] = emailItem
                if self._mOnReadItem is not None and \
                        not self._mOnReadItem(emailItem, folderItem, folderItem.mAccount, curIndex, totalCount):
                    return readCount
                readCount += 1
                if readCount < 0:
                    return readCount  # to do test
        Logger.d(appModel.getAppTag(), f"[{folderItem.mName}] end {readCount}/{len(folder.Items)} emails")
        return readCount

    def _readFilterFolders(self, folders, emailFilter: EmailFilter) -> int:
        readCount = 0
        for folder in folders:
            if not emailFilter.folders or folder.name in emailFilter.folders:
                readCount += self._readFilterEmails(folder, emailFilter)
            self._readFilterFolders(folder.folders, emailFilter)
        return readCount

    def _readFolders(self, folders, accountItem):
        totalCount = len(folders)
        curIndex = 0
        for folder in folders:
            curIndex += 1
            folderItem = FolderItem(folder, accountItem)
            self._mFolders[folderItem.mID] = folderItem
            if self._mOnReadItem is not None and \
                    not self._mOnReadItem(None, folderItem, accountItem, curIndex, totalCount):
                return
            self._readFolders(folder.folders, accountItem)
        return

    def _initAccountsForWindows(self):
        Logger.i(appModel.getAppTag(), f"begin")
        import pythoncom
        import win32com.client
        try:
            pythoncom.CoInitialize()
            outlookObject = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            accountsObject = win32com.client.Dispatch("Outlook.Application").Session.Accounts

            # init all folders
            if len(self._mAccounts) == 0 and outlookObject is not None:
                totalCount = len(accountsObject)
                curIndex = 0
                for account in accountsObject:
                    curIndex += 1
                    accountItem = AccountItem(account, outlookObject)
                    self._mAccounts[accountItem.mID] = accountItem
                    if self._mOnReadItem is not None and \
                            not self._mOnReadItem(None, None, accountItem, curIndex, totalCount):
                        return self._mAccounts, self._mFolders
                    inbox = outlookObject.Folders(account.DeliveryStore.DisplayName)
                    self._readFolders(inbox.Folders, accountItem)
        except Exception as e:
            Logger.e(appModel.getAppTag(), f"exception: {e}")
            return self._mAccounts, self._mFolders

        Logger.i(appModel.getAppTag(), f"end")
        return self._mAccounts, self._mFolders

    def _readFoldersMac(self, folders, accountItem):
        totalCount = len(folders)
        curIndex = 0
        for folder in folders:
            curIndex += 1
            folderItem = FolderItem(FolderObjectMac(folder["_id"], folder["_name"]), accountItem)
            self._mFolders[folderItem.mID] = folderItem
            if self._mOnReadItem is not None and \
                    not self._mOnReadItem(None, folderItem, accountItem, curIndex, totalCount):
                return
            self._readFoldersMac(folder["_folders"], accountItem)
        return

    def _initAccountsForMac(self):
        cacheFilePath = os.path.join(self.sLocalFolderBase, "cacheAccounts.json")
        cachedOnly = appModel.readConfig(self.__class__.__name__, "OnlyCachedAccounts", False)
        if cachedOnly:
            accounts = FileUtility.loadJsonFile(cacheFilePath)
        else:
            import applescript
            scriptFile = appModel.getScriptFile("getAllFolders.applescript")

            # write filter params
            appleParams = [
                "" + os.linesep,  # account filter: abc@def.com
                "" + os.linesep,  # to recipient filter: webex-android-support@cisco.com
            ]
            fw = open(os.path.join(SystemHelper.desktopPath(), "as_params.cfg"), "w")
            fw.writelines(appleParams)
            Logger.i(appModel.getAppTag(), f"appleParams={appleParams}")
            fw.close()
            asRead = applescript.run(scriptFile)
            os.remove(fw.name)
            accounts = json.loads(asRead.out)
            FileUtility.saveJsonFile(cacheFilePath, accounts)

        totalCount = len(accounts)
        curIndex = 0
        for account in accounts:
            curIndex += 1
            accountItem = AccountItem(AccountObjectMac(account["_name"]), accounts)
            self._mAccounts[accountItem.mID] = accountItem
            if self._mOnReadItem is not None and \
                    not self._mOnReadItem(None, None, accountItem, curIndex, totalCount):
                return self._mAccounts, self._mFolders
            self._readFoldersMac(account["_folders"], accountItem)
        appModel.saveConfig(self.__class__.__name__, "OnlyCachedAccounts", cachedOnly)
        return self._mAccounts, self._mFolders

    def initAccounts(self) -> Tuple[dict[str, AccountItem], dict[str, FolderItem]]:
        if SystemHelper.isWindows():
            return self._initAccountsForWindows()
        elif SystemHelper.isMac():
            return self._initAccountsForMac()
        else:
            Logger.e(appModel.getAppTag(), "Unsupported OS.")
            return self._mAccounts, self._mFolders

    def _readFilterItemsWindows(self, emailFilter: EmailFilter) -> dict[str, EmailItem]:
        Logger.i(appModel.getAppTag(), "begin")
        # filter mail
        for accountID, accountItem in self._mAccounts.items():
            account = accountItem.mAccountObject
            outlook = accountItem.mOutlook
            inbox = outlook.Folders(account.DeliveryStore.DisplayName)
            self._readFilterFolders(inbox.Folders, emailFilter)
        Logger.i(appModel.getAppTag(), "end")
        return self._mFilterMails

    def _queryMailsViaAppleScript(self, emailFilter: EmailFilter) -> [str, EmailItem]:
        cachedOnly = appModel.readConfig(self.__class__.__name__, "OnlyCachedMails", False)
        if cachedOnly:
            emailsFromAS = []
        else:
            import applescript
            scriptFile = appModel.getScriptFile("getMails.applescript")
            # write filter params
            emailFilterForAS = copy.deepcopy(emailFilter)
            self._correctFilter(emailFilterForAS)
            appleParams = [
                "" + os.linesep,                             # account filter: abc@def.com
                emailFilterForAS.folders[0] + os.linesep,    # folder filter: abc@def.com
                DateTimeHelper.getTimestampString(emailFilterForAS.beginDate, "%Y-%m-%d %H:%M:%S") + os.linesep,
                DateTimeHelper.getTimestampString(emailFilterForAS.endDate, "%Y-%m-%d %H:%M:%S") + os.linesep,
                self.sLocalFolderBase + os.linesep,
                ]
            fw = open(os.path.join(SystemHelper.desktopPath(), "as_params.cfg"), "w")
            fw.writelines(appleParams)
            Logger.i(appModel.getAppTag(), f"appleParams={appleParams}")
            fw.close()
            asRead = applescript.run(scriptFile)
            os.remove(fw.name)
            emailsFromAS = json.loads(asRead.out)
        appModel.saveConfig(self.__class__.__name__, "OnlyCachedMails", cachedOnly)
        return emailsFromAS

    def _readFilterItemsMac(self, emailFilter: EmailFilter) -> dict[str, EmailItem]:
        Logger.i(appModel.getAppTag(), "begin")

        cacheFilePath = os.path.join(self.sLocalFolderBase, "cacheMails.json")
        # first, load cache from file
        emailsFromCache = FileUtility.loadJsonFile(cacheFilePath)
        Logger.i(appModel.getAppTag(), f"emailsFromCache={len(emailsFromCache)}")
        if len(emailsFromCache) == 0:
            emailsFromCache = []
        # second, read new record via applescript
        emailsFromAS = self._queryMailsViaAppleScript(emailFilter)
        Logger.i(appModel.getAppTag(), f"emailsFromAS={len(emailsFromAS)}")
        # merge them
        emails = emailsFromAS + emailsFromCache
        FileUtility.saveJsonFile(cacheFilePath, emails)
        Logger.i(appModel.getAppTag(), f"emails={len(emails)}")

        # filter mail
        totalCount = len(emails)
        curIndex = 0
        for emailInfo in emails:
            curIndex += 1
            email = emailInfo["_mails"]
            receivedTime = EmailObjectMac.getReceivedTime(email["_receivedTime"]).timestamp()
            if emailFilter.beginDate != 0 and receivedTime < emailFilter.beginDate:
                continue
            if emailFilter.endDate != 0 and receivedTime > emailFilter.endDate:
                continue
            folderItem = self._mFolders[email["_folderID"]]
            emailItem = EmailItem(EmailObjectMac(email),
                                  folderItem, self.sLocalFolderBase)
            # special for mac begin
            emailItem.mAttachments = []
            for attachmentInfo in email["_attachments"]:
                try:
                    emailItem.mAttachments.append(attachmentInfo["_path"])
                except Exception:
                    pass
            # special for mac end
            self._mFilterMails[emailItem.mID] = emailItem
            if self._mOnReadItem is not None and \
                    not self._mOnReadItem(emailItem, folderItem, folderItem.mAccount, curIndex, totalCount):
                return self._mFilterMails
        Logger.i(appModel.getAppTag(), "end")
        return self._mFilterMails

    def readFilterItems(self, emailFilter: EmailFilter) -> dict[str, EmailItem]:
        beginTime = DateTimeHelper.getTimestampString(emailFilter.beginDate, None)
        endTime = DateTimeHelper.getTimestampString(emailFilter.endDate, None)
        Logger.i(appModel.getAppTag(), f"begin {beginTime} ~ {endTime}")

        self._mFilterMails.clear()
        if SystemHelper.isWindows():
            self._readFilterItemsWindows(emailFilter)
        elif SystemHelper.isMac():
            self._readFilterItemsMac(emailFilter)
            self._saveFilterMailsSummary(emailFilter)
        else:
            Logger.e(appModel.getAppTag(), "Unsupported OS.")
            return {}
        # sort it
        self._mFilterMails = {
            k: v for k, v in sorted(self._mFilterMails.items(),
                                    key=lambda item: item[1].mReceivedTime,
                                    reverse=True)
        }
        return self._mFilterMails

    def getAccounts(self) -> dict[str, AccountItem]:
        return self._mAccounts

    def getFolders(self) -> dict[str, FolderItem]:
        return self._mFolders

    def _saveFilterMailsSummary(self, emailFilter: EmailFilter):
        filterSummary = {
            "mailCount": len(self._mFilterMails),
            "filterFolders": emailFilter.folders,
            "filterTos": emailFilter.tos,
            "filterSenders": emailFilter.senders,
            "filterReceivers": emailFilter.receivers}
        if len(self._mFilterMails) > 0:
            mailsList = list(self._mFilterMails.items())
            filterSummary["filterBegin"] = mailsList[len(mailsList)-1][1].mReceivedTime.timestamp()
            filterSummary["filterEnd"] = mailsList[0][1].mReceivedTime.timestamp()
        else:
            filterSummary["filterBegin"] = emailFilter.beginDate
            filterSummary["filterEnd"] = emailFilter.endDate
        FileUtility.saveJsonFile(os.path.join(self.sLocalFolderBase, "emailFilter.json"), filterSummary)
        return

    def _correctFilter(self, emailFilter: EmailFilter) -> bool:
        # all mails have been stored if return False
        filterSummary = FileUtility.loadJsonFile(os.path.join(self.sLocalFolderBase, "emailFilter.json"))
        if "filterBegin" not in filterSummary or "filterEnd" not in filterSummary:
            return True

        filterBegin = filterSummary["filterBegin"]
        filterEnd = filterSummary["filterEnd"]
        if filterEnd < filterBegin:
            return True

        if emailFilter.endDate > filterEnd:
            if emailFilter.beginDate > filterEnd:
                # all mails have not been stored
                return True
            elif emailFilter.beginDate >= filterBegin:
                emailFilter.beginDate = filterEnd + 1
            else:
                # beyond range...
                emailFilter.beginDate = filterEnd + 1
        elif emailFilter.endDate >= filterBegin:
            if emailFilter.beginDate >= filterBegin:
                # all mails have not been stored, return False
                return False
            else:
                emailFilter.endDate = filterBegin - 1
        else:
            # all mails have not been stored
            return True

        return False
