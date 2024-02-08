#!/usr/bin/python3
import os
from dotenv import load_dotenv 
from sqlalchemy import create_engine, or_, desc, asc
from models.vote import Vote
from models.voter import Voter
from models.basemodel import Base
from sqlalchemy.orm import sessionmaker, scoped_session
from models.candidate import Candidate
from models.portfolio import Portfolio
from models.vote import Vote
from models.voter import Voter

load_dotenv()


class DBStorage():
    """Database Storage"""
    __engine = None
    __session = None

    def __init__(self):
        """Initializes the object"""
        user = os.getenv('USER')
        passwd = os.getenv('VOTEPASSWD')
        host = os.getenv('HOST')
        database = os.getenv('DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                                      .format(user, passwd, host, database))
        
    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session
    
    def db_session(self):
        return self.__session

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    def get_voter(self, email, token):
        voter = self.__session.query(Voter).filter((Voter.email == email) & (Voter.token == token)).first()
        if voter:
            return voter
        return False

    def get_candidates(self):
        candidates_grouped = (
            self.__session.query(Candidate)
            .order_by(asc(Candidate.portfolio_id), desc(Candidate.candidateId))
            .all())
        grouped_candidates = {}
        
        for candidate in candidates_grouped:
            portfolio_name = candidate.portfolio.portfolioName
            
            if portfolio_name not in grouped_candidates:
                grouped_candidates[portfolio_name] = []

            grouped_candidates[portfolio_name].append(candidate)

        return grouped_candidates



    def cast_vote(self, voter_id, candidate_id, portfolio_id):
        """
            Returns voteConfirmationNumber if vote successful.
        """
        number = self.__session.query(Voter).count()
        voteConfirmationNumber = str(20000 + number)
        if voter_id and candidate_id and portfolio_id:
            new_vote = Vote(
                candidateId=candidate_id,
                voteConfirmationNumber=voteConfirmationNumber,
                portfolioId=portfolio_id,
                voterId=voter_id)    
            self.__session.add(new_vote)
            self.save()
            return voteConfirmationNumber
        return None
    
    def register_voter(self, first_name=None, last_name=None, email=None, pwdhash=None, contact=None):
        """
            returns None if voter exist, voter_id on success
        """
        if first_name and last_name and email and pwdhash and contact:
            new_voter = Voter(
                first_name=first_name,
                last_name=last_name,
                email=email,
                passwordhash=pwdhash,
                contact=contact
            )
            self.__session.add(new_voter)
            self.save()
            return new_voter
        else:
            raise TypeError("missing argument")
    
    
    def add_portfolio(self, pname):
        """
            Create portfolios to the database
        """
        porfolio_does_not_exist = not(self.__session.query(Portfolio).filter(
            Portfolio.portfolioName == pname).first())
        if porfolio_does_not_exist:
            portfolio_id = (100 + self.__session.query(Portfolio).count())
            new_portfolio = Portfolio(
                portfolioName=pname,
                portfolioId=portfolio_id)
            self.__session.add(new_portfolio)
            self.save()
            return portfolio_id
        return None
    
    def register_candidate(self, first_name, last_name, contact,
                           email, porfolio_name, photo_url=None, 
                           bio=None, manifesto=None):
        """
            Returns None if the portfolio or candidate exits, else create an new candidate
        """
        if not self.check_existance(email=email, contact=contact, type="Candidate"):
            porfolio_exist = (self.__session.query(Portfolio).filter(
                Portfolio.portfolioName == porfolio_name).first())
            portfolio_id = str(porfolio_exist.portfolioId)
            if porfolio_exist:
                new_candidate = Candidate(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    contact=contact,
                    photo_url=photo_url,
                    portfolio_id=portfolio_id,
                    bio=bio,
                    manifesto=manifesto)
                self.__session.add(new_candidate)
                self.save()
                return new_candidate.candidateId
            return None
        return None
    
    def check_existance(self, contact, email, type):
        # check if user exists in the database
        classes = {"Voter": Voter, "Candidate": Candidate}
        if type not in classes.keys():
            raise TypeError(f"Type: '{type}' does not exist")
        class_type = classes[type]
        voter_exist = self.__session.query(class_type).filter(
            or_(class_type.contact == contact, class_type.email == email)).first()
        if voter_exist:
            return True
        else:
            return False           
        
#vote = db.get_vote("76ab0ecf-7a39-40f9-9084-ad9040b040d6")

#if vote:
    # Assuming there is a one-to-many relationship between Voter and Vote
#    if vote.candidate:  # Iterating over the list of votes
#        print("Candidate name: ", vote.candidate.first_name, vote.candidate.last_name)
#        print("Portfolio:", vote.candidate.portfolio.portfolioName)

        
        # Add more attributes as needed
#else:
#    print("No voter found for the given ID.")

