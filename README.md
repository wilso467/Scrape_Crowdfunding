# Scrape_Crowdfunding

KEY DESIGN ELEMENTS

Kickstarter makes it's unsuccessful projects unsearchable, though the pages themselves persist.  In order to have a representative data set, the code periodically searches Kickstarter for new projects and keeps a log of the projects it finds.  Later, a separate command uses Selenium and PhantomJS to search the projects in the log file for the desired data.

