from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from commons.Utility import Utilities
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import itertools


class Webutilities:

    def __init__(self, driver):
        self.driver = driver
        self.util_obj = Utilities()

    def set_value(self, locator, value):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            element.clear()
            element.click()
            element.send_keys(value)
        except Exception as e:
            print(e.args)
            return False

    def get_value(self, locator):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            return element.text or element.get_attribute("value") or element.get_attribute("data")
        except Exception as e:
            print(e.args)
            return False

    def click(self, locator):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            element.click()
        except Exception as e:
            print(e.args)
            return False

    def select(self, locator, value):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            Select(element).select_by_visible_text(value)
        except Exception as e:
            print(e.args)
            return False

    def return_elements(self, locator):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            return element.find_elements(By.XPATH, locator)
        except Exception as e:
            print(e.args)
            return False

    def get_table(self, locator):
        try:
            element = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, locator)))
            return element
        except Exception as e:
            print(e.args)
            return False

    def get_table_rows(self, locator):
        try:
            element = self.get_table(locator)
            rows = element.find_elements(By.TAG_NAME, "tr")
            return rows
        except Exception as e:
            print(e.args)
            return False

    def get_table_data(self, locator):
        try:
            td_data = []
            tbl_rows = self.get_table_rows(locator)
            for rows in tbl_rows:
                tbl_col = rows.find_elements_by_tag_name('td')
                td_data.append([td.text for td in tbl_col])
            return td_data
        except Exception as e:
            print(e.args)
            return False

    def check_element_exist(self, locator):
        try:
            element = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, locator)))
            return True
        except (NoSuchElementException, TimeoutException) as e:
            return False

    def replace_suffix(self, address):
        try:
            suffix_option = ["ALY", "ANX", "AVE", "BCH", "BND", "BLF", "BLFS", "BLVD", "BR", "BRG", "BRK", "BRKS", "BYP", "CP", "CPE", "CSWY", "CTRS", "CIR", "CIRS", "CLF", "CLFS", "CLB", "CMN", "COR", "CORS", "CRSE",
                                 "CT", "CV", "CVS", "CRK", "CRES", "CRST", "XING", "XRD", "CURV", "DV", "DR", "DRS", "EST", "ESTS", "EXPY", "EXT", "EXTS", "FRY", "FLD", "FLDS", "FRD", "FRST", "FRG", "FRGS", "FRK", "FRKS",
                                 "FT", "GDN", "GDNS", "GTWY", "GLN", "GLNS", "GRN", "GRNS", "GRV", "GRVS", "HBR", "HBRS", "HVN", "HTS", "HWY", "HL", "HLS", "HOLW", "INLT", "IS", "ISLE", "JCT", "JCTS", "KY", "KYS", "LK",
                                 "LKS", "LAND", "LNDG", "LN", "LGT", "LGTS", "LF", "LCK", "LCKS", "LDG", "LOOP", "MALL", "MNR", "MNRS", "MDW", "MDWS", "ML", "MLS", "MSN", "MTWY", "MT", "MTN", "MTNS", "NCK", "ORCH", "OPAS",
                                 "PARK", "PKWY", "PASS", "PSGE", "PATH", "PIKE", "PNE", "PNES", "PL", "PLN", "PLNS", "PLZ", "PT", "PTS", "PRT", "PRTS", "RAMP", "RNCH", "RST", "RDG", "RDGS", "RIV", "RD", "RDS", "RTE", "ROW",
                                 "RUE", "RUN", "SHL", "SHLS", "SHR", "SHRS", "SPG", "SPGS", "SPUR", "SQ", "SQS", "STA", "STRM", "ST", "STS", "TER", "TRWY", "TRCE", "TRAK", "TRFY", "TRL", "TUNL", "TPKE", "UPAS", "UN", "UNS",
                                 "VLY", "VLYS", "VIA", "VW", "VWS", "VLG", "VLGS", "VL", "VIS", "WALK", "WALL", "WAY", "WAYS", "WL", "WLS"]
            suffix_value = ["Alley", "Annex", "Avenue", "Beach", "Bend", "Bluff", "Bluffs", "Boulevard", "Branch", "Bridge", "Brook", "Brooks", "Bypass", "Camp", "Cape", "Causeway", "Centers", "Circle", "Circles",
                                "Cliff", "Cliffs", "Club", "Common", "Corner", "Corners", "Course", "Court", "Cove", "Coves", "Creek", "Crescent", "Crest", "Crossing", "Crossroad", "Curve", "Divide", "Drive", "Drives",
                                "Estate", "Estates", "Expressway", "Extension", "Extensions", "Ferry", "Field", "Fields", "Ford", "Forest", "Forge", "Forges", "Fork", "Forks", "Fort", "Garden", "Gardens", "Gateway", "Glen",
                                "Glens", "Green", "Greens", "Grove", "Groves", "Harbor", "Harbors", "Haven", "Heights", "Highway", "Hill", "Hills", "Hollow", "Inlet", "Island", "Isle", "Junction", "Junctions", "Key", "Keys",
                                "Lake", "Lakes", "Land", "Landing", "Lane", "Light", "Lights", "Loaf", "Lock", "Locks", "Lodge", "Loop", "Mall", "Manor", "Manors", "Meadow", "Meadows", "Mill", "Mills", "Mission", "Motorway",
                                "Mount", "Mountain", "Mountains", "Neck", "Orchard", "Overpass", "Park", "Parkway", "Pass", "Passage", "Path", "Pike", "Pine", "Pines", "Place", "Plain", "Plains", "Plaza", "Point", "Points",
                                "Port", "Ports", "Ramp", "Ranch", "Rest", "Ridge", "Ridges", "River", "Road", "Roads", "Route", "Row", "Rue", "Run", "Shoal", "Shoals", "Shore", "Shores", "Spring", "Springs", "Spur",
                                "Square", "Squares", "Station", "Stream", "Street", "Streets", "Terrace", "Throughway", "Trace", "Track", "Trafficway", "Trail", "Tunnel", "Turnpike", "Underpass", "Union", "Unions", "Valley",
                                "Valleys", "Viaduct", "View", "Views", "Village", "Villages", "Ville", "Vista", "Walk", "Wall", "Way", "Ways", "Well", "Wells"]
            inx = 0
            for suffix in suffix_value:
                if str(suffix).lower() in str(address).lower():
                    address = address.replace(suffix.upper(), suffix_option[inx]).replace(suffix, suffix_option[inx])
                    print(address)
                    break
                else:
                    inx = inx + 1
            return address
        except Exception as e:
            print(e.args)
            return False

    def replace_pre_directions(self, direction):
        try:
            pre_dir_option = ['E', 'W', 'N', 'S']
            pre_dir_value = ['EAST', 'WEST', 'NORTH', 'SOUTH']
            inx = 0
            for pre in pre_dir_value:
                if str(pre).lower() in str(direction).lower():
                    direction = direction.replace(direction, pre_dir_option[inx])
                    print(direction)
                    break
                else:
                    inx = inx + 1
            return direction
        except Exception as e:
            print(e.args)
            return False

    def address_format(self, owner_address):
        try:
            add_list = ['USPSBoxType', 'USPSBoxID', 'AddressNumber', 'StreetNamePreDirectional', 'StreetName', 'StreetNamePostType', 'OccupancyIdentifier', 'PlaceName', 'StateName', 'ZipCode']
            not_add_list = ['AddressNumber', 'StreetName', 'PlaceName', 'StateName', 'ZipCode']
            for list_val in not_add_list:
                if list_val not in owner_address:
                    owner_address[list_val] = list_val

            owner_address_val = ''
            for list_val in add_list:
                if list_val in owner_address:
                    if 'StreetNamePostType' in owner_address and list_val == 'StreetNamePostType':
                        street_name_post = self.replace_suffix(owner_address['StreetNamePostType'])
                        owner_address_val = owner_address_val + ' ' + street_name_post
                    elif 'OccupancyIdentifier' in owner_address and list_val == 'OccupancyIdentifier':
                        occupancy_identifier = owner_address['OccupancyIdentifier']
                        owner_address_val = owner_address_val + ' #' + self.util_obj.string_without_specialchars(occupancy_identifier)
                    elif 'StreetNamePreDirectional' in owner_address and list_val == 'StreetNamePreDirectional':
                        pre_directions = self.replace_pre_directions(owner_address['StreetNamePreDirectional'])
                        owner_address_val = owner_address_val + ' ' + pre_directions
                    else:
                        owner_address_val = owner_address_val + ' ' + owner_address[list_val]

            return owner_address_val
        except Exception as e:
            print(e.args)

    def address_format_with_fields(self, owner_address, address_info, address_type):
        try:
            add_list = ['USPSBoxType', 'USPSBoxID', 'AddressNumber', 'StreetNamePreDirectional', 'StreetName', 'StreetNamePostType', 'StreetNamePostDirectional', 'OccupancyIdentifier', 'PlaceName', 'StateName', 'ZipCode']
            not_add_list = ['PlaceName', 'StateName', 'ZipCode']

            for list_val in not_add_list:
                if list_val not in owner_address:
                    owner_address[list_val] = list_val
            if 'Recipient' in owner_address:
                address_info['CareOfName'] = owner_address['Recipient'].replace('C/O', '')

            if address_type.lower() == 'mail':
                for list_val in add_list:
                    if list_val in owner_address:

                        if 'USPSBoxType' in owner_address and list_val == 'USPSBoxType':
                            address_info['AddrStreetName'] = owner_address['USPSBoxType'] + ' ' + owner_address['USPSBoxID']
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + address_info['AddrStreetName']
                            continue

                        if 'AddressNumber' in owner_address and list_val == 'AddressNumber':
                            if '-' in owner_address['AddressNumber']:
                                address_info['AddrHse1Nbr'] = owner_address['AddressNumber'].split('-')[0]
                                address_info['AddrHse2Nbr'] = owner_address['AddressNumber'].split('-')[1]
                                address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + address_info['StdAddr1'] + ' ' + owner_address['AddressNumber']
                                continue
                            else:
                                address_info['AddrHse1Nbr'] = owner_address['AddressNumber']
                                address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + owner_address['AddressNumber']
                                continue

                        if 'StreetNamePreDirectional' in owner_address and list_val == 'StreetNamePreDirectional':
                            pre_directions = self.replace_pre_directions(owner_address['StreetNamePreDirectional'])
                            address_info['AddrDirLeftCd'] = pre_directions
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + pre_directions
                            continue

                        if 'StreetName' in owner_address and list_val == 'StreetName':
                            address_info['AddrStreetName'] = owner_address['StreetName']
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + owner_address['StreetName']
                            continue

                        if 'StreetNamePostType' in owner_address and list_val == 'StreetNamePostType':
                            street_name_post = self.replace_suffix(owner_address['StreetNamePostType'])
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + street_name_post
                            continue

                        if 'StreetNamePostDirectional' in owner_address and list_val == 'StreetNamePostDirectional':
                            post_directions = self.replace_pre_directions(owner_address['StreetNamePostDirectional'])
                            address_info['AddrDirRightCd'] = post_directions
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + post_directions
                            continue

                        if 'OccupancyIdentifier' in owner_address and list_val == 'OccupancyIdentifier':
                            occupancy_identifier = owner_address['OccupancyIdentifier']
                            address_info['AddrAptNbr'] = '#' + self.util_obj.string_without_specialchars(occupancy_identifier)
                            address_info['StdAddr1'] = address_info['StdAddr1'] + ' ' + address_info['AddrAptNbr']
                            continue

                        if 'PlaceName' in owner_address and list_val == 'PlaceName':
                            address_info['StdCityName'] = owner_address['PlaceName']
                            continue

                        if 'StateName' in owner_address and list_val == 'StateName':
                            address_info['StdStCd'] = owner_address['StateName']
                            continue

                        if 'ZipCode' in owner_address and list_val == 'ZipCode':
                            address_info['StdZipCd'] = owner_address['ZipCode']
                            continue
            elif address_type.lower() == 'situs':
                for list_val in add_list:
                    if list_val in owner_address:

                        if 'USPSBoxType' in owner_address and list_val == 'USPSBoxType':
                            address_info['SitusAddrStreetName'] = owner_address['USPSBoxType'] + ' ' + owner_address['USPSBoxID']
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + address_info['SitusAddrStreetName']
                            continue

                        if 'AddressNumber' in owner_address and list_val == 'AddressNumber':
                            if '-' in owner_address['AddressNumber']:
                                address_info['SitusAddrHse1Nbr'] = owner_address['AddressNumber'].split('-')[0]
                                address_info['SitusAddrHse2Nbr'] = owner_address['AddressNumber'].split('-')[1]
                                address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + address_info['SitusAddrHse1Nbr'] + ' ' + owner_address['SitusAddrHse2Nbr']
                                continue
                            else:
                                address_info['SitusAddrHse1Nbr'] = owner_address['AddressNumber']
                                address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + owner_address['AddressNumber']
                                continue

                        if 'StreetNamePreDirectional' in owner_address and list_val == 'StreetNamePreDirectional':
                            pre_directions = self.replace_pre_directions(owner_address['StreetNamePreDirectional'])
                            address_info['SitusAddrDirLeftCd'] = pre_directions
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + pre_directions
                            continue

                        if 'StreetName' in owner_address and list_val == 'StreetName':
                            address_info['SitusAddrStreetName'] = owner_address['StreetName']
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + owner_address['StreetName']
                            continue

                        if 'StreetNamePostType' in owner_address and list_val == 'StreetNamePostType':
                            street_name_post = self.replace_suffix(owner_address['StreetNamePostType'])
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + street_name_post
                            continue

                        if 'StreetNamePostDirectional' in owner_address and list_val == 'StreetNamePostDirectional':
                            post_directions = self.replace_pre_directions(owner_address['StreetNamePostDirectional'])
                            address_info['SitusAddrDirRightCd'] = post_directions
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + post_directions
                            continue

                        if 'OccupancyIdentifier' in owner_address and list_val == 'OccupancyIdentifier':
                            occupancy_identifier = owner_address['OccupancyIdentifier']
                            address_info['SitusAddrAptNbr'] = '#' + self.util_obj.string_without_specialchars(occupancy_identifier)
                            address_info['SitusStdAddr'] = address_info['SitusStdAddr'] + ' ' + address_info['SitusAddrAptNbr']
                            continue

                        if 'PlaceName' in owner_address and list_val == 'PlaceName':
                            address_info['SitusStdCityName'] = owner_address['PlaceName']
                            continue

                        if 'StateName' in owner_address and list_val == 'StateName':
                            address_info['SitusStdStCd'] = owner_address['StateName']
                            continue

                        if 'ZipCode' in owner_address and list_val == 'ZipCode':
                            address_info['SitusStdZipCd'] = owner_address['ZipCode']
                            continue

            return address_info
        except Exception as e:
            print(e.args)

    def dblclick(self, locator):
        try:
            element = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, locator)))
            element.click()
            actions = ActionChains(self.driver)
            actions.move_to_element(element).double_click(element).perform()
        except Exception as e:
            print(e.args)
            return False

    def clickByName(self, locator):
        try:
            element = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.NAME, locator)))
            element.click()
        except Exception as e:
            print(e.args)
            return False

    def selectcombo(self, locator, addlocator, fieldlist):
        try:
            element = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, locator)))
            mySelect=Select(element)
            for o in mySelect.options:
                if o.text in fieldlist:
                    o.click()
                    self.click(addlocator)
            #Select(element).select_by_visible_text(value)
        except Exception as e:
            print(e.args)
            return False

    def getTable(self, locator):
        try:
            element = WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.XPATH, locator)))
            return element
        except Exception as e:
            print(e.args)
            return False

    def getRows(self, locator):
        try:
            element = self.getTable(locator)
            rows = element.find_elements(By.TAG_NAME, "tr")
            return rows
        except Exception as e:
            print(e.args)
            return False

    def get_table_headers(self, locator):
        try:
            td_data = []
            tbl_rows = self.get_table_rows(locator)
            for rows in tbl_rows:
                tbl_col = rows.find_elements_by_tag_name('th')
                td_data.append([td.text for td in tbl_col])
                break
            return td_data
        except Exception as e:
            print(e.args)
            return False

    def get_table_header_data(self, locator):
        try:
            td_data = []
            tbl_rows = self.get_table_rows(locator)
            for rows in tbl_rows:
                tbl_header = rows.find_elements_by_xpath("./*")
                row_inc = 1
                for tbl_data in tbl_header:
                    if tbl_data.tag_name == 'th':
                        if row_inc < len(tbl_header) and tbl_header[row_inc].tag_name == 'td':
                            td_data.append(tbl_data.text + ': ' + tbl_header[row_inc].text)
                    row_inc = row_inc + 1
            return td_data
        except Exception as e:
            print(e.args)
            return False

    def tear_down(self):
        self.driver.close()

    def close_all_windows(self):
        windows = self.driver.window_handles
        for inc in windows:
            self.driver.switch_to.window(inc)
            self.driver.close()
