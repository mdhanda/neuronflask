import csv
import pandas as pd
import time

import utilities.constants as const
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


from utilities.utils import Utils



class Neuron(webdriver.Chrome):
    logger = Utils.ilogger()
    mongoClient = Utils.iclient()

    def __init__(self, teardown=False):
        self.teardown = teardown

        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-sh-usage')
        option.add_experimental_option('excludeSwitches', ['enable-logging']) # Need it to run through cmd-line

        #super(Neuron, self).__init__(service=Service(ChromeDriverManager().install()), options=option)
        super(Neuron, self).__init__(service=Service(const.DRIVER_PATH), options=option)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def load_page(self, pageURL):
        self.get(pageURL)
        try:
            parent = self.current_window_handle
            uselessWindows = self.window_handles
            for winId in uselessWindows:
                if winId != parent:
                    self.switch_to.window(winId)
                    self.close()
        except (NoSuchWindowException, StaleElementReferenceException) as e:
            # print(e)
            self.logger.error('In elements, Unable to locate Course Image.', exc_info=True)
            courseImage.append(None)
        self.logger.debug('Selenium driver Get URL: '+pageURL)

    def scroll_to_bottom(self):
        previous_height = self.execute_script('return document.body.scrollHeight')

        while True:
            self.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(3)
            new_height = self.execute_script('return document.body.scrollHeight')
            if (new_height == previous_height):
                break
            previous_height = new_height
            # break # temporary, need to be removed
        self.logger.debug('URL Page - loading all content by scrolling to bottom')

    def load_all_items(self):
        self.courses = self.find_elements(by=By.XPATH,
                                       value="//*[@class='AllCourses_course-filter__14bMO']//descendant::div[@class='Course_flex__3ZrIo flex']")
        self.logger.debug('URL Page - extracting all elements using driver.find_elements()')

    def save_to_csv(self):
        courseImage = []
        courseTitle = []
        courseLink = []
        courseDesc = []
        courseInstructor = []
        coursePrice = []


        for count, course in enumerate(self.courses, start=1):

            try:
                courseImage.append(
                    course.find_element(by=By.XPATH, value=".//div/img[@alt='course-image']").get_attribute("src"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                #print(e)
                self.logger.error('In elements, Unable to locate Course Image.', exc_info=True)
                courseImage.append(None)

            try:
                courseTitle.append(
                    course.find_element(by=By.XPATH, value=".//div[@class='Course_right-area__1XUfi']/a/h5").get_attribute(
                        "innerText"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                self.logger.error('In elements, Unable to locate Course Title.', exc_info=True)
                courseTitle.append(None)

            try:
                courseLink.append(
                    course.find_element(by=By.XPATH, value=".//div[@class='Course_right-area__1XUfi']/a").get_attribute(
                        "href"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                self.logger.error('In elements, Unable to locate Course Link.', exc_info=True)
                courseLink.append(None)

            try:
                courseDesc.append(
                    course.find_element(by=By.XPATH, value=".//div[@class='Course_course-desc__2G4h9']").get_attribute(
                        "innerText"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                self.logger.error('In elements, Unable to locate Course Description.', exc_info=True)
                courseDesc.append(None)

            try:
                courseInstructor.append(course.find_element(by=By.XPATH,
                                                            value=".//div[@class='Course_course-instructor__1bsVq']").get_attribute(
                    "innerText"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                self.logger.error('In elements, Unable to locate Course Instructor.', exc_info=True)
                courseInstructor.append(None)

            try:
                coursePrice.append(course.find_element(by=By.XPATH,
                                                       value=".//div[@class='Course_course-price__3-3_U']/h6").get_attribute(
                    "innerText"))
            except (NoSuchElementException, StaleElementReferenceException) as e:
                self.logger.error('In elements, Unable to locate Course Price.', exc_info=True)
                coursePrice.append(None)

        courseDataFrame = pd.DataFrame(
            {'image': courseImage, 'title': courseTitle, 'link': courseLink, 'desc': courseDesc, 'instructor': courseInstructor,
             'price': coursePrice})
        self.logger.info('Total'+str(len(courseDataFrame))+' courses found.')

        try:
            self.logger.debug('Trying to save to ' + const.CSV_FILENAME + ' file.')
            courseDataFrame.to_csv(const.CSV_FILENAME, sep=';', encoding="utf-16", index=False)
        except Exception as e:
            self.logger.error('CSV Save failed.', exc_info=True)
        print(courseDataFrame)

    def save_to_mongo(self):

        def readCSV(csvPath):
            dict_data_list = []
            try:
                with open(csvPath, 'r', encoding="utf-16") as f:
                    courses_data = csv.reader(f, delimiter='\n')


                    for index, item in enumerate(courses_data):
                        if index == 0:
                            header_list = list(item[0].split(';'))
                        else:
                            data_list = list(item[0].split(';'))
                            res = dict(zip(header_list, data_list))
                            dict_data_list.append(res)
            except Exception as e:
                self.logger.error('Read CSV failed.', exc_info=True)

            return dict_data_list

        itemList = readCSV(const.CSV_FILENAME)

        print('########################')
        print(itemList)
        try:
            self.mongoClient.insert_many(itemList)
        except Exception as e:
            #print("Error : {} ".format(e))
            self.logger.error('Mongo insertion failed.', exc_info=True)

    def load_courses_from_mongo(self):
        self.courses = self.find_elements(by=By.XPATH,
                                       value="//*[@class='AllCourses_course-filter__14bMO']//descendant::div[@class='Course_flex__3ZrIo flex']")
        self.logger.debug('URL Page - extracting all elements using driver.find_elements()')

    def load_course_detail(self):
        courseObjectives = self.find_elements(by=By.XPATH,
                                       value="//*[@class='CourseLearning_card__WxYAo card']//descendant::li")
        self.objectives = [i.text for i in courseObjectives]
        courseRequirements = self.find_elements(by=By.XPATH,
                                       value="//*[@class='CourseRequirement_card__3g7zR requirements card']//descendant::li")
        self.requirements = [i.text for i in courseRequirements]

        #Solution 1
        #self.execute_script("arguments[0].click();", WebDriverWait(self, 20).until(
        #    EC.element_to_be_clickable((By.XPATH, "//*[@class='CurriculumAndProjects_view-more-btn__3ggZL']"))))
        #Solution 2
        #self.implicitly_wait(10)
        #spanElement = self.find_element(by=By.XPATH, value="//*[@class='CurriculumAndProjects_view-more-btn__3ggZL']")
        #spanElement.location_once_scrolled_into_view
        #spanElement.click()

        courseCurriculam = self.find_elements(by=By.XPATH,
                                       value="//*[@class='CurriculumAndProjects_accordion-header__3ALRY CurriculumAndProjects_flex__1-ljx flex']//descendant::span")
        self.curriculam = [i.text for i in courseCurriculam]

        courseFeatures = self.find_elements(by=By.XPATH,
                                       value="//*[@class='CoursePrice_course-features__2qcJp']//descendant::li")
        self.features = [i.text for i in courseFeatures]


        self.logger.debug(", ".join(self.objectives))
        self.logger.debug(", ".join(self.requirements))
        self.logger.debug(", ".join(self.curriculam))
        self.logger.debug(", ".join(self.features))

        self.logger.debug('URL Page - extracting all elements using driver.find_elements()')
