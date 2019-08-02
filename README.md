# ebay-manager
I made this for personal use and I'll probably completely change the functionality in the future, which is why I decided not to unit test anything.

To run it, use a Python shell that won't close once it's done executing, such as IDLE. You have to type in the functions yourself just like in a shell.

Here's a list of all functions available to the user:

save(file_name: str)
load(file_name: str)
reset()

deposit(dollars: float)
withdraw(dollars: float)
earn(dollars: float)
spend(dollars: float)
clock(hours_spent: float)
summary()

branch(num_or_name: Union\[int, str\]) -> \_BranchInterface
branch_names()
branch_descriptions()
branch_summaries()

\_BranchInterface.name(self)
\_BranchInterface.description(self)
\_BranchInterface.rename(self, name: str)
\_BranchInterface.describe(self, description: str)

\_BranchInterface.summary(self)
\_BranchInterface.deposit(self, dollars: float)
\_BranchInterface.withdraw(self, dollars: float)
\_BranchInterface.earn(self, dollars: float)
\_BranchInterface.spend(self, dollars: float)
\_BranchInterface.clock(self, hours_spent: float)

\_BranchInterface.inventory(self)
\_BranchInterface.item(self, num_or_name: Union\[int, str\]) -> \_ItemInterface

\_BranchInterface.split(self, ways: int)
\_BranchInterface.merge(self, other: \_BranchInterface)

\_ItemInterface.units(units: int)
\_ItemInterface.relabel(label: str)
\_ItemInterface.acquire()
\_ItemInterface.discard()
\_ItemInterface.buy(dollars_spent: float)
\_ItemInterface.sell(dollars_earned: float)

history()
