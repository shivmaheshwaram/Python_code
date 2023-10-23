from commons.webUtility import Webutilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pathlib
from datetime import datetime, timedelta, date
import pytz
from pytz import timezone
from commons.webUtility import Webutilities
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from commons.Utility import Utilities
from Value_verifictaion.VVApplFunctions import VVApplUtilities, get_logger
import time
log = get_logger("Sales Force:")


class SalesForce:
    def __init__(self, icp):
        self.utilObj = Utilities()
        driver = webdriver.Chrome()
        self.qc_config_jsonData = self.utilObj.get_json_data('\JsonData\qcconfig.json')
        driver.get(self.qc_config_jsonData['sf_url'])
        driver.maximize_window()
        self.driver = driver
        self.webObj = Webutilities(driver)
        self.icp = icp

    def create_a_new_view(self, viewname, fieldname, filtervalue, fieldslst):
        """Create a new view in sales force"""
        self.webObj.click("// a[contains(text(), 'Create New View')]")
        self.webObj.set_value("//input[@id='fname']", viewname)
        self.webObj.select("//select[@id='fcol1']", fieldname)
        self.webObj.set_value("//input[@id='fval1']", filtervalue)
        self.webObj.selectcombo("//select[@id='colselector_select_0']", "//img[@class='rightArrowIcon']", fieldslst)
        self.webObj.click("//div[@class='pbHeader']//input[@name='save']")

    def sales_force_login(self, user_name, password):
        try:
            self.webObj.set_value("//input[@id='username']", user_name)
            self.webObj.set_value("//input[@id='password']", password)
            self.webObj.click("//input[@id='Login']")
            if self.webObj.check_element_exist("//span[contains(text(),'EDG Lightning')]"):
                log.info("Salesforce webpage is in Lightning mode. Reverting it to Classic")
                self.webObj.click("//span[@class='uiImage']")
                time.sleep(2)
                self.webObj.click("//a[@class='profile-link-label switch-to-aloha uiOutputURL']")
                time.sleep(5)
            else:
                log.info("Salesforce webpage is in Classic mode")
        except Exception as e:
            log.info(e.args)

    def search_icp(self):
        try:
            self.webObj.set_value("//*[@id='phSearchInput']", self.icp)
            time.sleep(2)
            self.webObj.click("//*[@id='searchButtonContainer']")
            time.sleep(2)
            self.webObj.click("//div[@id='Assessor_Production__c_body']//a[contains(text()," + self.icp + ")]")
            time.sleep(2)
        except Exception as e:
            log.info(e.args)

    def search_inquiries_icp(self, inq_icp):
        try:
            self.webObj.set_value("//*[@id='phSearchInput']", inq_icp)
            self.webObj.click("//*[@id='searchButtonContainer']")
            self.webObj.click("//div[@id='Inquiries__c_body']//a[contains(text(),'" + inq_icp + "')]")
        except Exception as e:
            log.info(e.args)

    def add_new_notes(self, note_title, note_body, is_private):
        try:
            # self.webObj.click("//span[@class='listTitle'][contains(text(),'Notes & Attachments')]")
            self.webObj.click("//input[@name='newNote']")
            if is_private.lower() == 'y':
                self.webObj.click("//input[@id='IsPrivate']")

            self.webObj.set_value("//input[@id='Title']", note_title)
            self.webObj.set_value("//textarea[@id='Body']", note_body)
            self.webObj.click("//td[@id='bottomButtonRow']//input[contains(@name,'save')]")

        except Exception as e:
            log.info(e.args)

    def upload_file_to_notes(self, upload_filename):
        try:
            self.webObj.click("//input[@name='attachFile']")
            self.driver.implicitly_wait(10)
            self.driver.find_element_by_xpath("//input[@id='file']").send_keys(upload_filename)
            self.driver.implicitly_wait(10)
            self.webObj.click("//input[@id='Attach']")
            self.webObj.click("//input[@name='cancel']")
        except Exception as e:
            log.info(e.args)

    def click_edit(self):
        try:
            self.webObj.click("//td[@id='topButtonRow']//input[@name='edit']")
        except Exception as e:
            log.info(e.args)

    def click_notes(self):
        try:
            self.webObj.click("//span[@class='listTitle'][contains(text(),'Notes & Attachments')]")
        except Exception as e:
            log.info(e.args)

    def update_viper_quality_review_qc(self, qc_status, db_stg, qc_date, qc_analyst, qc_pick_date, qc_complete,
                                       otd_date, cnty_prod, qc_fix, viper_fix):
        self.click_edit()
        self.webObj.select("//select[@id='00N400000024wto']", qc_status)
        self.webObj.set_value("//input[@id='00N33000002r8ca']", db_stg)
        self.webObj.set_value("//input[@id='00N33000002zFeJ']", qc_date)
        self.webObj.select("//select[@id='00N33000002qzxU']", qc_analyst)
        self.webObj.set_value("//input[@id='00N400000024wtc']", qc_pick_date)
        self.webObj.set_value("//input[@id='00N400000024wtV']", qc_complete)
        self.webObj.set_value("//input[@id='00N400000024wsh']", otd_date)
        self.webObj.set_value("//input[@id='00N400000024wrR']", cnty_prod)
        self.webObj.select("//select[@id='00N400000024wtY']", qc_fix)
        self.webObj.select("//select[@id='00N400000024wtp']", viper_fix)
        self.webObj.click("//td[@id='bottomButtonRow']//input[@name='save']")

    def tear_down(self):
        self.webObj.tear_down()

    def salesforce_anualicp_verify_valueverification_field_status(self):
        """Use this function to verify the value verification field value on ICP page"""
        try:
            valueverification = self.webObj.get_value("//div[@id='00N400000024wvS_ileinner']")
            valueverification = valueverification.replace(" ", "")
            if valueverification != "":
                return valueverification
            else:
                return ""

        except Exception as e:
            log.info(e.args)
            return ""

    def salesforce_capture_requireddetails_from_anualicp(self):
        """Use this function to capture all the required data from the given anual ICP page"""
        try:
            productiontype = self.webObj.get_value("//div[@id='00N400000024wtL_ileinner']")
            version = self.webObj.get_value("//div[@id='00N400000024wvU_ileinner']")
            countyfip = self.webObj.get_value("//div[@id='00N4000000259tW_ileinner']")
            log.info(countyfip)
            arr = countyfip.split(",")
            county = arr[0]
            state = (arr[1]).replace(' ', '')
            fips = (arr[2]).replace(' ', '')
            tier = self.webObj.get_value("//div[@id='00Nf3000003SBwi_ileinner']")
            edition = self.webObj.get_value("//div[@id='00N400000024ws3_ileinner']")
            taxyear = self.webObj.get_value("//div[@id='00N400000024wvA_ileinner']")
            countywebsite = self.webObj.get_value("//div[@id='00N400000024wrS_ileinner']")
            icpactdetails = f'{productiontype}|{countyfip}|{version}|{county}|{edition}|{tier}|{state}|{taxyear}|{countywebsite}|{fips}'
            # log.info("Capture the required details from the given anual icp: " + icpactdetails)
            return icpactdetails
        except Exception as e:
            log.info(e.args)
            return ""

    def salesforce_anual_icp_verification(self, ptype, version):
        """Use this function to verify the production type value whether its fall under the VV process"""
        try:
            ptype = ptype.upper() #'FULL PRODUCTION/TAX UPDATE'
            actptype = ['FULL PRODUCTION', 'FULL PRODUCTION/TAX UPDATE', 'FULL PRODUCTION/PRELIM',
                        'POST TAX UPDATE', 'PRELIMINARY VALUES',
                        'TAX & VALUE UPDATE',
                        'TAX & VALUE UPDATE IN LIEU OF FP', 'VALUE/TAX/PCL INSERT', 'VALUE UPDATE',
                        'SUPPLEMENTAL - VALUES',
                        'SUPPLEMENTAL - TAXES']
            nouseptype = ['FULL PRODUCTION/PRELIM',
                          'PRELIMINARY VALUES', 'TAX & VALUE UPDATE',
                          'TAX & VALUE UPDATE IN LIEU OF FP', 'VALUE/TAX/PCL INSERT',
                          'VALUE UPDATE', 'SUPPLEMENTAL - VALUES', 'SUPPLEMENTAL - TAXES']

            for item in actptype:
                for x in nouseptype:
                    if x == item:
                        return 1
                if ptype == "FULL PRODUCTION" and int(version) > 1:
                    return 2
                elif actptype.count(ptype) == 0:
                    return 1
                else:
                    return 0
        except Exception as e:
            log.info(e.args)
            return 1

    def create_new_icp(self, icpvalues):
        try:
            child_window_handle = self.driver.current_window_handle
            arrdata = icpvalues.split("|")
            self.webObj.click("//td[@id='topButtonRow']//input[@name='submit_inquiry']")
            self.driver.switch_to.window(self.driver.window_handles[1])
            # """Enter all the required fields"""
            # Title
            self.webObj.set_value("//input[@id='j_id0:j_id2:j_id3:j_id7:j_id8']",
                                  f'{arrdata[3]}, {arrdata[6]} ({self.icp}) - Value Verification')
            # MLS Priority
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id14']", "2")
            # Inquiry Category
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id20']", "Value Verification")
            # Inquiry Departmrnt
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id21']", "Data Acquisition")
            # Processing Team
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id22']", "Cognizant")
            # Priority
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id24']", "1 - Required for this edition")
            # Business Liaison
            self.webObj.select("//select[@id='j_id0:j_id2:j_id3:j_id7:j_id28']", "Erin Miranda")
            # Description
            self.webObj.set_value("//textarea[@id='j_id0:j_id2:j_id3:j_id40:j_id41']",
                                  "For Testing purpose. Please ignore")
            # Cancel
            # self.webObj.click("//input[contains(@name,'j_id0:j_id2:j_id3:j_id4:bottom:j_id6')]")
            # Save
            self.webObj.click("//input[contains(@name,'j_id0:j_id2:j_id3:j_id4:bottom:j_id5')]")
            newicp = self.webObj.get_value("// div[ @ id = 'Name_ileinner']")
            self.driver.close()
            self.driver.switch_to.window(child_window_handle)
            return newicp

        except Exception as e:
            log.info(e.args)

    def attach_valueverificationform_to_newicp(self, newicp, attachment):
        """Use this function to upload an attachment to the given ICP"""
        try:
            self.inquiry_icp(newicp)
            self.webObj.click("//input[@name='attachFile']")
            self.driver.implicitly_wait(10)
            self.driver.find_element_by_xpath("//input[@id='file']").send_keys(attachment)
            self.driver.implicitly_wait(10)
            self.webObj.click("//input[@id='Attach']")
            self.webObj.click("//input[@name='cancel']")
            # log.info("Attach the file i.e " + attachment + " to the new inquiry " + newicp)
        except Exception as e:
            log.info(e.args)

    def enter_finalnotes_to_newicp(self, msg, url, taxyear, attachment):
        """ Enter the final notes for the new icp as part of the VV process"""
        try:
            title = "Automation Submission Note: " + self.get_pst_date_twodigit_fullyear()
            if msg == "":
                status = "Yes"
            else:
                status = "No"
            actmsg = "Website URLs used for VV: " + url
            actmsg += "\n\nIs value verification completely done from the given county website:-" + status
            actmsg += "\n\nDescription: All " + taxyear + "- values and taxes has been verified from above given county site"
            if status == "No":
                actmsg += "\n\nNote: " + msg
            if attachment.find("|") > 0:
                attachment = attachment.split("|")
                i = 1
                actmsg += "\n\nAttachment Files:-\n"
                while i <= len(attachment):
                    actmsg += "\n" + str(i) + ". " + pathlib.Path(attachment[i - 1]).name
                    i = i + 1
            else:
                actmsg += "\n\nAttachment Files:-\n" + pathlib.Path(attachment).name

            self.webObj.click("//input[@name='newNote']")
            self.webObj.set_value("//input[@id='Title']", title)
            self.webObj.set_value("//textarea[@id='Body']", actmsg)
            self.webObj.click("//td[@id='topButtonRow']//input[@name='save']")
            # log.info("Enter the notes successfully")
        except Exception as e:
            log.info(e.args)

    def select_from_dropdown(self, locator, locator2, value):
        """Select a value from a rich text box in Sales Force"""
        try:
            element = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.ID, locator)))
            element.click()
            actions = ActionChains(self.driver)
            actions.move_to_element(element).double_click(element).perform()
            element2 = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, locator2)))
            element2.click()
            element2 = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, locator2)))
            Select(element2).select_by_value(value)
            element2.click()
        except Exception as e:
            log.info(e.args)
            return False

    def update_valueverification_value(self, newinquiry):
        """Use this function to update the new inquiry number in the Value verification field under the annual icp"""
        try:
            self.search_icp()
            # self.webObj.click("//li[@id='01r400000001vL1_Tab']//a[contains(text(),'Assessor Production')]")
            # time.sleep(1)
            # self.webObj.click("//span[@class='fFooter']//a[contains(text(),'Edit')]")
            # time.sleep(2)
            # self.webObj.set_value("//input[@id='fval1']", self.icp)
            # self.webObj.clickByName("save")
            # time.sleep(3)
            # self.webObj.click("//div[@class='x-grid3-cell-inner x-grid3-col-NAME']//span[contains(text()," + self.icp + ")]")
            self.webObj.dblclick("//td[@id='00N400000024wvS_ilecell']")
            time.sleep(2)
            self.webObj.click("//div[@id='00N400000024wvS_ileinner']")
            time.sleep(1)
            self.webObj.set_value("//input[@id='00N400000024wvS']", newinquiry)
            time.sleep(2)
            self.webObj.click("//td[@id='topButtonRow']//input[@name='inlineEditSave']")
            time.sleep(2)
        # log.info("Updated the new inquiry value " + newinquiry + " at the 'Value Verification ICP#' field successfully")
        except Exception as e:
            log.info(e.args)

    def get_pst_date_twodigit_fullyear(self):
        date_format = 'X%m/X%d/X%Y'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))
        today = date.strftime(date_format).replace('X0', 'X').replace('X', '')
        return today

    def inquiry_icp(self, newicp):
        """Use this function to upload an attachment to the given ICP"""
        try:
            self.webObj.click("(//a[contains(text(),'Inquiries')])[1]")   #//a[contains(text(),'Inquiries')]
            time.sleep(2)
            self.webObj.click("//span[@class='fFooter']//a[contains(text(),'Edit')]")
            time.sleep(2)
            self.webObj.set_value("//input[@id='fval1']", newicp)
            self.webObj.click("(//input[@class='btn primary'])[2]")
            time.sleep(3)
            chk_icpelmt = self.webObj.check_element_exist("//div[@class='x-grid3-cell-inner x-grid3-col-NAME']//span[contains(text()," + newicp + ")]")
            if chk_icpelmt:
                self.webObj.click("//div[@class='x-grid3-cell-inner x-grid3-col-NAME']//span[contains(text()," + newicp + ")]")
                time.sleep(3)
        except Exception as e:
            log.info(e.args)

    def update_thestatus_on_newicp(self, newicp, status):
        """Use this function to update the vv status for the new icp"""
        try:
            self.webObj.dblclick("//div[@id='00Nf3000003NnBZ_ileinner']")
            time.sleep(2)
            self.webObj.click("//select[@id='00Nf3000003NnBZ']")
            time.sleep(2)
            self.webObj.click("//option[contains(text(),'Verified on Website')]")
            time.sleep(2)
            # self.webObj.click("//td[@id='topButtonRow']//input[@name='inlineEditSave']")

            if status == "":
                self.webObj.dblclick("//div[@id='00N400000024wJh_ileinner']")
                time.sleep(2)
                self.webObj.click("//select[@id='00N400000024wJh']")
                time.sleep(2)
                self.webObj.select("//select[@id='00N400000024wJh']", "Complete")
                time.sleep(2)
                self.webObj.click("//td[@id='topButtonRow']//input[@name='inlineEditSave']")
                time.sleep(2)
            else:
                self.webObj.dblclick("//div[@id='00N400000024wJJ_ileinner']")
                time.sleep(2)
                self.webObj.click("//select[@id='00N400000024wJJ']")
                time.sleep(2)
                self.webObj.click("//option[contains(text(),'Joel Kollin')]")
                time.sleep(2)
                # self.webObj.select("//select[@id='00N400000024wJJ']", "Joel Kollin")
                self.webObj.dblclick("//div[@id='00N400000024wJh_ileinner']")
                time.sleep(1)
                self.webObj.click("//select[@id='00N400000024wJh']")
                time.sleep(2)
                self.webObj.click("//option[contains(text(),'Pending Inquirer Acceptance')]")
                time.sleep(2)
                # self.webObj.select("//select[@id='00N400000024wJh']", "Pending Inquirer Acceptance")
                self.webObj.click("//td[@id='topButtonRow']//input[@name='inlineEditSave']")
                time.sleep(2)

        except Exception as e:
            log.info(e.args)

    def tearDown(self):
        self.driver.close()

# if __name__ == '__main__':

# sf_obj = SalesForce('95537')
# sf_obj.sales_force_login('sgorentla@corelogic.com.config1', 'Officemax!100')
# sf_obj.search_icp()
# sf_obj.search_icp()
# # sf_obj.add_new_notes()
# sf_obj.upload_file_to_notes("C:\\Users\\Sgorentla\\Desktop\\Automation\\Python_Projects\\VA_Giles_0712\\Data\\qc_report_va_giles_540.xlsx")
# sf_obj.update_viper_quality_review_qc('Complete to Production', '7/14/2019', '7/18/2019', 'Cognizant2-YA', '7/18/2019', '7/18/2019', '11/30/2018', '7/20/2019', 'No', 'No')

# //input[@name='attachFile']